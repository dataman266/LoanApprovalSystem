"""Unified MCP Server - Aggregates all MCP services"""

import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.logger import get_logger
from src.mcp.services.applicant_db import mcp as applicant_db_mcp
from src.mcp.services.risk_rules import mcp as risk_rules_mcp
from src.mcp.services.decision_synthesis import mcp as decision_synthesis_mcp
from src.mcp.services.notification_system import mcp as notification_system_mcp

logger = get_logger(__name__)

app = FastAPI(title="MCP Server Aggregator")


# Tool request model
class ToolRequest(BaseModel):
    params: dict = {}


@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok"}


# ApplicantDB routes
@app.post("/applicant_db/get_applicant_profile")
def get_applicant_profile(request: ToolRequest):
    try:
        result = applicant_db_mcp._tools[0].func(**request.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/applicant_db/get_credit_history")
def get_credit_history(request: ToolRequest):
    try:
        result = applicant_db_mcp._tools[1].func(**request.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/applicant_db/get_employment_history")
def get_employment_history(request: ToolRequest):
    try:
        result = applicant_db_mcp._tools[2].func(**request.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/applicant_db/validate_application_completeness")
def validate_application_completeness(request: ToolRequest):
    try:
        result = applicant_db_mcp._tools[3].func(**request.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# RiskRules routes
@app.post("/risk_rules/calculate_dti")
def calculate_dti(request: ToolRequest):
    try:
        result = risk_rules_mcp._tools[0].func(**request.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/risk_rules/detect_anomalies")
def detect_anomalies(request: ToolRequest):
    try:
        result = risk_rules_mcp._tools[2].func(**request.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/risk_rules/get_risk_thresholds")
def get_risk_thresholds(request: ToolRequest):
    try:
        result = risk_rules_mcp._tools[4].func()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# DecisionSynthesis routes
@app.post("/decision_synthesis/apply_decision_rules")
def apply_decision_rules(request: ToolRequest):
    try:
        result = decision_synthesis_mcp._tools[0].func(**request.params)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting unified MCP aggregator server on port 8005")
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")
