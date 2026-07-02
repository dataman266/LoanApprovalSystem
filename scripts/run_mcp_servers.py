#!/usr/bin/env python3
"""Start all MCP servers concurrently"""

import subprocess
import sys
import time
from pathlib import Path

# Change to project root
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

MCP_SERVICES = {
    "applicant_db": {
        "module": "src.mcp.services.applicant_db",
        "port": 8001,
        "name": "ApplicantDB",
    },
    "risk_rules": {
        "module": "src.mcp.services.risk_rules",
        "port": 8002,
        "name": "RiskRules",
    },
    "decision_synthesis": {
        "module": "src.mcp.services.decision_synthesis",
        "port": 8003,
        "name": "DecisionSynthesis",
    },
    "notification_system": {
        "module": "src.mcp.services.notification_system",
        "port": 8004,
        "name": "NotificationSystem",
    },
}

processes = {}


def start_mcp_server(service_key, service_config):
    """Start a single MCP server"""
    module = service_config["module"]
    port = service_config["port"]
    name = service_config["name"]

    cmd = [
        sys.executable,
        "-c",
        f"from {module} import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port={port}, log_level='error')",
    ]

    print(f"Starting {name} on port {port}...")
    process = subprocess.Popen(
        cmd,
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    processes[service_key] = process
    return process


def main():
    print("🚀 Starting MCP Servers...")
    print("=" * 60)

    # Start all MCP servers
    for service_key, config in MCP_SERVICES.items():
        start_mcp_server(service_key, config)
        time.sleep(1)

    print("\n✅ All MCP servers started:")
    for service_key, config in MCP_SERVICES.items():
        print(f"   • {config['name']:25} http://localhost:{config['port']}")

    print("\n⏳ Waiting for servers (Ctrl+C to stop)...")

    try:
        # Wait for processes
        while True:
            for service_key, process in list(processes.items()):
                if process.poll() is not None:  # Process exited
                    print(f"\n❌ {MCP_SERVICES[service_key]['name']} crashed!")
                    sys.exit(1)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping MCP servers...")
        for process in processes.values():
            process.terminate()
        for process in processes.values():
            process.wait(timeout=5)
        print("✅ All servers stopped")


if __name__ == "__main__":
    main()
