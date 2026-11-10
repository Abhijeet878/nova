# 🌌 NOVA — Autonomous Multi-Agent Automation Platform
> **Problem Statement 1: Agentic AI for Automation**  
> *"Build autonomous AI agents that reason, plan, collaborate, and act with minimal human intervention."*

---

## 🌟 What is NOVA?
**NOVA** (**N**ext-generation **O**rchestration, **V**erification & **A**ction) is a 100% local, autonomous multi-agent platform powered by **LangGraph**, **Ollama (`qwen2.5:3b`)**, and **Docker**.

Unlike traditional AI wrappers that just chat or hallucinate success, NOVA operates with **complete data privacy** and features an independent **Verification & Self-Healing Engine** that physically audits outcomes on disk.

```
[ User Goal ] 
     │
     ▼
[ Planner Agent ] 
     │
     ▼
[ Executor Agent (Tools) ] 
     │
     ▼
[ Verifier Agent (Physical Disk Audit) ] 
     ├── [✅ Passed] ──► [Audited Deliverable]
     └── [❌ Failed] ──► [🔄 Recovery Engine (Self-Heal & Retry)]
```

---

## ✨ Key Differentiators for Hackathon Judges
1. **🛡️ 100% Data Sovereignty:** Operates locally on CPU. Zero cloud dependencies, zero external API keys, zero token fees.
2. **🔍 Tamper-Proof Verification:** Doesn't just say *"I did it"*. It cryptographically checks file hashes, sizes, and disk counts.
3. **🔄 Autonomous Recovery:** Automatically catches tracebacks, adapts the plan, and self-heals up to 3 retry loops.
4. **🐳 One-Command Turnkey Deployment:** Runs on any machine via Docker Compose.

---

## 🚀 Quick Start

### 1. Prerequisites
- [Ollama](https://ollama.com/download) installed
- Model pulled:
  ```powershell
  ollama pull qwen2.5:3b
  ```

### 2. Fast Local Launch
```powershell
# Clone the repository
git clone https://github.com/YOUR_USERNAME/nova.git
cd nova

# Install dependencies
pip install -r requirements.txt

# Start the dashboard
python frontend/app.py
```
Open **`http://localhost:7860`** in your browser.

### 3. Docker Deployment
```powershell
docker compose up --build
```

---

## 👥 Team & Architecture
- **Member A (Lead & Infra):** Docker, Ollama local host, config, integration
- **Member B (Frontend):** Gradio Live Intelligence Dashboard & Observability
- **Member C (Agent Architect):** LangGraph state machine & multi-agent routing
- **Member D (Tools & Integrity):** Sandboxed tools & Physical Disk Verifier
