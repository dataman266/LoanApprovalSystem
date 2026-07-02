"""API routes for loan application processing"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from src.models.schemas import (
    LoanApplicationRequest,
    ApplicationStatusResponse,
    ApplicationHistoryResponse,
)
from src.models.database import LoanApplication
from src.database import get_db
from src.orchestration.graph import process_loan_application
from src.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["applications"])


def _serialize_trace(trace_item: dict) -> dict:
    """Convert trace timestamp to ISO format"""
    trace_copy = dict(trace_item)
    if 'timestamp' in trace_copy and hasattr(trace_copy['timestamp'], 'isoformat'):
        trace_copy['timestamp'] = trace_copy['timestamp'].isoformat()
    return trace_copy


def _serialize_model_output(output_model) -> dict:
    """Serialize Pydantic model to JSON-safe dict"""
    return output_model.model_dump(mode='json') if output_model else None


def _update_application_results(db_app: LoanApplication, result_state: dict) -> None:
    """Update database application record with processing results"""
    db_app.applicant_profile = _serialize_model_output(result_state["applicant_profile"])
    db_app.financial_risk = _serialize_model_output(result_state["financial_risk"])
    db_app.decision = _serialize_model_output(result_state["decision"])
    db_app.compliance_check = _serialize_model_output(result_state["compliance_check"])

    if result_state["decision"]:
        db_app.final_decision_status = result_state["decision"].classification

    db_app.execution_trace = [_serialize_trace(t) for t in result_state["execution_trace"]]
    db_app.error_log = result_state["error_log"]
    db_app.status = "completed" if result_state["final_status"] != "error" else "error"
    db_app.completed_at = result_state["completed_at"]


@router.post("/applications")
async def submit_application(
    request: LoanApplicationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Submit a new loan application for processing"""

    application_id = request.applicant_id

    logger.info(
        "Application received",
        application_id=application_id,
        applicant_name=request.applicant_name,
    )

    db_app = LoanApplication(
        id=application_id,
        applicant_id=application_id,
        applicant_name=request.applicant_name,
        input_data=request.model_dump(mode='json'),
        status="processing",
        created_at=datetime.utcnow(),
    )

    db.add(db_app)
    db.commit()

    logger.info("Application record created", application_id=application_id)

    try:
        background_tasks.add_task(
            _process_application_background,
            application_id,
            request.applicant_id,
            request,
        )
        logger.info("Application queued for processing", application_id=application_id)

    except Exception as e:
        logger.error("Queueing error", application_id=application_id, error=str(e))
        db_app.status = "error"
        db_app.error_log = [str(e)]
        db_app.completed_at = datetime.utcnow()
        db.commit()

    return {"application_id": application_id, "status": "processing"}


def _process_application_background(
    application_id: str,
    applicant_id: str,
    request: LoanApplicationRequest,
):
    """Process application in background"""
    from src.database import SessionLocal
    db = SessionLocal()
    try:
        db_app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
        if not db_app:
            return

        result_state = process_loan_application(
            application_id,
            applicant_id,
            request,
        )
        _update_application_results(db_app, result_state)
        db.commit()
        logger.info("Application processed", application_id=application_id, status=db_app.status)
    except Exception as e:
        logger.error("Background processing error", application_id=application_id, error=str(e))
        db_app.status = "error"
        db_app.error_log = [str(e)]
        db_app.completed_at = datetime.utcnow()
        db.commit()
    finally:
        db.close()


def _get_application_or_404(application_id: str, db: Session) -> LoanApplication:
    """Retrieve application or raise 404 HTTPException"""
    db_app = db.query(LoanApplication).filter(LoanApplication.id == application_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_app


@router.get("/applications/{application_id}", response_model=ApplicationStatusResponse)
async def get_application_status(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Get the status and result of a loan application"""

    db_app = _get_application_or_404(application_id, db)

    result = None
    if db_app.decision:
        from src.models.schemas import DecisionOutput
        result = DecisionOutput(**db_app.decision)

    return ApplicationStatusResponse(
        application_id=db_app.id,
        status=db_app.status,
        created_at=db_app.created_at,
        completed_at=db_app.completed_at,
        result=result,
        error=" ".join(db_app.error_log) if db_app.error_log else None,
    )


@router.get("/applications/{application_id}/history", response_model=ApplicationHistoryResponse)
async def get_application_history(
    application_id: str,
    db: Session = Depends(get_db),
):
    """Get complete application history with execution trace"""

    db_app = _get_application_or_404(application_id, db)

    decision = None
    if db_app.decision:
        from src.models.schemas import DecisionOutput
        decision = DecisionOutput(**db_app.decision)

    return ApplicationHistoryResponse(
        application_id=db_app.id,
        applicant_id=db_app.applicant_id,
        status=db_app.status,
        created_at=db_app.created_at,
        completed_at=db_app.completed_at,
        decision=decision,
        execution_trace=db_app.execution_trace or [],
    )


@router.get("/applications")
async def list_applications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all applications with pagination"""

    applications = (
        db.query(LoanApplication)
        .offset(skip)
        .limit(limit)
        .all()
    )

    return [
        {
            "application_id": app.id,
            "applicant_id": app.applicant_id,
            "status": app.status,
            "created_at": app.created_at,
            "completed_at": app.completed_at,
        }
        for app in applications
    ]
