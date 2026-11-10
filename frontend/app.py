"""
FRONTEND DASHBOARD — Gradio Live Agent Intelligence Console for NOVA
=====================================================================
WHAT IT DOES:
    Provides a visual dashboard for the hackathon demo:
    - User types a goal or picks a preset scenario.
    - Shows step-by-step progress through the LangGraph state machine.
    - Displays the Verification Audit Proof (real evidence from disk).
"""

import gradio as gr
import json
from backend.app.graph.workflow import autopilot_app

def run_agent_workflow(goal: str):
    """
    Invokes the LangGraph State Machine and yields live progress to the UI.
    """
    if not goal or not goal.strip():
        return "Please enter a valid goal.", "No plan generated.", "Awaiting execution."

    initial_state = {
        "user_request": goal,
        "plan": [],
        "current_step": 0,
        "execution_result": "",
        "verification": {"passed": False, "expected": "", "actual": "", "details": ""},
        "retry_count": 0,
        "error_message": "",
        "final_report": "",
        "status": "starting",
        "messages": []
    }

    # Run the graph
    final_output_state = autopilot_app.invoke(initial_state)

    # Format Plan View
    plan_text = "### 📋 Formulated Execution Plan:\n"
    for step in final_output_state.get("plan", []):
        icon = "✅" if step["status"] == "completed" else ("❌" if step["status"] == "failed" else "⏳")
        plan_text += f"- **Step {step['step_id']}**: {step['description']} [{icon} {step['status'].upper()}]\n"

    # Format Evidence/Verification View
    verif = final_output_state.get("verification", {})
    verif_text = "### 🔍 Physical Disk Verification Proof:\n"
    verif_text += f"- **Status**: {'✅ PASSED (Tamper-Proof Proof)' if verif.get('passed') else '⚠️ ANOMALY DETECTED'}\n"
    verif_text += f"- **Expected**: {verif.get('expected', 'N/A')}\n"
    verif_text += f"- **Actual Physical Disk Audit**: {verif.get('actual', 'N/A')}\n"
    verif_text += f"- **Audit Details**: {verif.get('details', 'N/A')}\n"
    verif_text += f"- **Self-Healing Retries Taken**: {final_output_state.get('retry_count', 0)}\n"

    # Deliverable summary
    deliverable = f"### 📦 Deliverables Generated in `./outputs/`:\n"
    deliverable += f"Execution Output Snippet:\n```json\n{final_output_state.get('execution_result', '{}')[:800]}\n```"

    return plan_text, verif_text, deliverable

# Gradio Interface Theme & Layout
with gr.Blocks(title="NOVA — Autonomous Agent Platform", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🌌 NOVA: Autonomous Agent Platform")
    gr.Markdown(
        "**N**ext-generation **O**rchestration, **V**erification & **A**ction\n\n"
        "*Plan ➔ Act ➔ Verify (Disk Audit) ➔ Recover (Self-Healing) ➔ Deliver (100% Local)*"
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            goal_input = gr.Textbox(
                label="🎯 What is the high-level goal for NOVA?",
                placeholder="e.g. Organize all workspace files, identify duplicates, and generate an audited summary.",
                lines=3
            )
            run_btn = gr.Button("⚡ Run Autonomous Agent Loop", variant="primary")
            
            gr.Markdown("### 💡 Quick Presets for Live Pitch:")
            preset_btn1 = gr.Button("📁 Preset 1: Auto-Organize Files & Detect Duplicates")
            preset_btn2 = gr.Button("🔍 Preset 2: Web Research & Competitive Briefing")
            preset_btn3 = gr.Button("📊 Preset 3: Analyze Data & Check Anomalies")
            
        with gr.Column(scale=3):
            plan_box = gr.Markdown("### 📋 Formulated Execution Plan:\n*Waiting for task...*")
            verif_box = gr.Markdown("### 🔍 Physical Disk Verification Proof:\n*Waiting for audit results...*")
            output_box = gr.Markdown("### 📦 Deliverables:\n*Waiting for execution...*")

    # Wire buttons
    run_btn.click(
        fn=run_agent_workflow,
        inputs=[goal_input],
        outputs=[plan_box, verif_box, output_box]
    )
    preset_btn1.click(
        lambda: "Organize all files in the workspace directory into categories and detect any duplicates.",
        outputs=[goal_input]
    )
    preset_btn2.click(
        lambda: "Research current breakthroughs in Agentic AI and write an executive briefing.",
        outputs=[goal_input]
    )
    preset_btn3.click(
        lambda: "Analyze data.csv, compute summary metrics, and report null column anomalies.",
        outputs=[goal_input]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
