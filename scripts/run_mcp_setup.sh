#!/bin/bash

# Quick setup for MCP servers

echo "🚀 MCP Server Setup"
echo "=================="

# Install FastMCP if needed
pip install -q fastmcp 2>/dev/null

# Create ports info file
cat > /tmp/mcp_ports.txt << 'PORTS'
ApplicantDB Server:        http://localhost:8001
RiskRules Server:          http://localhost:8002
DecisionSynthesis Server:  http://localhost:8003
NotificationSystem Server: http://localhost:8004
MCP Aggregator:            http://localhost:8005
PORTS

echo ""
echo "📡 MCP Servers Configuration:"
cat /tmp/mcp_ports.txt

echo ""
echo "✅ Setup complete. You can now:"
echo "   1. Start individual MCP servers:"
echo "      python3 -c \"from src.mcp.services.applicant_db import mcp; import uvicorn; uvicorn.run(mcp.app, port=8001)\""
echo ""
echo "   2. Or start all via orchestration (they're already integrated)"
echo ""
