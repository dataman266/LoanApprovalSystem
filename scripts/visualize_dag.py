#!/usr/bin/env python3
"""Visualize LangGraph DAG"""

import sys
sys.path.insert(0, '/home/ubuntu/Desktop/Assignment')

from src.orchestration.graph import create_loan_approval_graph

def visualize_dag():
    graph = create_loan_approval_graph()

    # Mermaid format
    mermaid = graph.get_graph().draw_mermaid()
    print("Mermaid Diagram (paste at https://mermaid.live):")
    print("=" * 70)
    print(mermaid)

    # Save to file
    with open('/home/ubuntu/Desktop/Assignment/DAG_MERMAID.md', 'w') as f:
        f.write("# LangGraph DAG Visualization\n\n")
        f.write("```mermaid\n")
        f.write(mermaid)
        f.write("\n```\n\n")
        f.write("## How to view:\n")
        f.write("1. Visit https://mermaid.live\n")
        f.write("2. Paste the diagram above\n")
        f.write("3. Or use VS Code Mermaid extension\n")

    print("\n✓ Saved to DAG_MERMAID.md")

    # Graph info
    print("\n" + "=" * 70)
    print("Graph Structure:")
    print("=" * 70)
    g = graph.get_graph()
    print(f"Nodes: {list(g.nodes.keys())}")
    print(f"Total nodes: {len(g.nodes)}")
    print("\nFlow: validate_input → profile_analysis → financial_risk → synthesis → compliance")

if __name__ == "__main__":
    visualize_dag()
