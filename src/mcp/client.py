"""MCP Client - Unified connection to all MCP servers"""

import json
import httpx
from typing import Dict, Any, List
from src.logger import get_logger

logger = get_logger(__name__)

# MCP Server endpoints
MCP_SERVERS = {
    "applicant_db": "http://localhost:8001",
    "risk_rules": "http://localhost:8002",
    "decision_synthesis": "http://localhost:8003",
    "notification_system": "http://localhost:8004",
}

TIMEOUT = 30.0


class MCPClient:
    """Unified MCP client for all server connections"""

    def __init__(self):
        self.client = httpx.Client(timeout=TIMEOUT)
        self._servers_available = {}
        self._check_servers()

    def _check_servers(self):
        """Check which MCP servers are available"""
        for server_name, url in MCP_SERVERS.items():
            try:
                response = self.client.get(f"{url}/docs", timeout=5.0)
                self._servers_available[server_name] = response.status_code == 200
                if self._servers_available[server_name]:
                    logger.info(f"MCP Server available: {server_name}")
            except Exception as e:
                self._servers_available[server_name] = False
                logger.warning(f"MCP Server unavailable: {server_name} - {str(e)}")

    def call_tool(self, server: str, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Call a tool on an MCP server.
        Falls back to mock if server unavailable.
        """
        if not self._servers_available.get(server, False):
            logger.warning(f"Using fallback for {server}.{tool_name}")
            return self._fallback_tool(server, tool_name, **kwargs)

        try:
            url = f"{MCP_SERVERS[server]}/tool/{tool_name}"
            response = self.client.post(url, json=kwargs)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MCP call failed: {server}.{tool_name} - {str(e)}")
            return self._fallback_tool(server, tool_name, **kwargs)

    def _fallback_tool(self, server: str, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Fallback to mock implementation if MCP server unavailable"""
        from src.mcp.mock_data import (
            generate_mock_applicant,
            generate_mock_credit_history,
            generate_mock_employment_history,
            generate_anomalies,
            get_risk_thresholds,
        )

        if server == "applicant_db":
            applicant_id = kwargs.get("applicant_id", "")
            if tool_name == "get_applicant_profile":
                applicant = generate_mock_applicant(applicant_id)
                return {
                    "applicant_id": applicant_id,
                    "age": applicant["age"],
                    "employment_type": applicant["employment_type"],
                    "current_annual_income": applicant["annual_income"],
                    "existing_monthly_liabilities": applicant["existing_liabilities"],
                }
            elif tool_name == "get_credit_history":
                history = generate_mock_credit_history(applicant_id)
                return {
                    "applicant_id": applicant_id,
                    "credit_score": history["credit_score"],
                    "late_payments_count": history["late_payments_count"],
                    "delinquencies": history["delinquencies"],
                    "accounts_opened": history["accounts_opened"],
                    "years_credit_history": history["years_credit_history"],
                    "credit_utilization_ratio": history["credit_utilization_ratio"],
                }
            elif tool_name == "get_employment_history":
                history = generate_mock_employment_history(applicant_id)
                return {
                    "applicant_id": applicant_id,
                    "total_employment_months": history["total_employment_months"],
                    "number_of_jobs": history["number_of_jobs"],
                    "current_employment_stability": history["current_employment_stability"],
                    "employment_history": history["employment_history"],
                }
            elif tool_name == "validate_application_completeness":
                flags = []
                if applicant_id.startswith("incomplete_"):
                    flags.append("missing_kyc_documents")
                completeness_score = 1.0 if not flags else 0.7
                return {
                    "applicant_id": applicant_id,
                    "is_complete": len(flags) == 0,
                    "completeness_score": completeness_score,
                    "flags": flags,
                }

        elif server == "risk_rules":
            applicant_id = kwargs.get("applicant_id", "")
            if tool_name == "calculate_dti":
                monthly_liab = kwargs.get("monthly_liabilities", 0)
                annual_income = kwargs.get("annual_income", 1)
                dti = (monthly_liab * 12) / annual_income
                return {"dti": dti, "dti_percentage": f"{dti*100:.1f}%"}
            elif tool_name == "detect_anomalies":
                applicant_data = kwargs.get("applicant_data", {})
                anomalies = generate_anomalies(applicant_data)
                return {"applicant_id": applicant_id, "anomalies": anomalies}
            elif tool_name == "get_risk_thresholds":
                return get_risk_thresholds()

        elif server == "decision_synthesis":
            if tool_name == "apply_decision_rules":
                return {
                    "decision": "Requires Manual Review",
                    "reason": "Rules applied",
                    "risk_score": 50.0,
                }

        return {"error": f"Unknown tool: {tool_name}"}


# Global MCP client instance
_mcp_client = None


def get_mcp_client() -> MCPClient:
    """Get or create global MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
