"""
STATE.PY — The LangGraph State Schema
=======================================
WHAT IT DOES:
    Defines the SHARED STATE that flows through the entire
    LangGraph workflow. Every agent node (Planner, Executor,
    Verifier, Recovery) reads from and writes to this state.

WHY IT EXISTS:
    In LangGraph, agents don't talk to each other directly.
    Instead, they ALL read/write to a shared state dictionary.
    Think of it as a shared whiteboard that every team member
    can see and update.

FOR JUDGES:
    "Our state schema is the single source of truth for the
    entire workflow. Every agent node reads the current state,
    performs its work, and updates the state. This makes the
    system fully observable and debuggable."

ANALOGY:
    Imagine a hospital patient chart:
    - Doctor writes diagnosis → chart updated
    - Nurse reads chart → administers medication → chart updated
    - Lab technician reads chart → runs tests → chart updated
    Everyone shares ONE chart. That's our AgentState.
"""

from typing import TypedDict, Literal, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class TaskStep(TypedDict):
    """A single step in the execution plan.
    
    Example:
        {
            "step_id": 1,
            "description": "Search for latest AI trends",
            "agent": "executor",
            "status": "completed",
            "result": "Found 5 relevant articles..."
        }
    """
    step_id: int                    # Sequential step number
    description: str                # What this step should do
    agent: str                      # Which agent handles this step
    status: str                     # "pending" | "running" | "completed" | "failed"
    result: str                     # Output from executing this step


class VerificationResult(TypedDict):
    """Result of the Verification Agent's check.
    
    Example:
        {
            "passed": False,
            "expected": "3 files should be created",
            "actual": "Only 2 files were created",
            "details": "Missing: summary.md"
        }
    """
    passed: bool                    # Did verification pass?
    expected: str                   # What we expected to happen
    actual: str                     # What actually happened
    details: str                    # Additional details


class AgentState(TypedDict):
    """
    THE CENTRAL STATE — shared by all agents in the workflow.
    
    This is the "whiteboard" that every agent reads and writes to.
    LangGraph passes this state from node to node automatically.
    
    ┌──────────────────────────────────────────────────────┐
    │                   AgentState                          │
    │                                                      │
    │  user_request: "Organize my downloads folder"        │
    │                                                      │
    │  plan: [                                             │
    │    {step 1: "Scan directory", status: "completed"},  │
    │    {step 2: "Categorize files", status: "running"},  │
    │    {step 3: "Move files", status: "pending"}         │
    │  ]                                                   │
    │                                                      │
    │  current_step: 2                                     │
    │  execution_result: "Found 50 files: 20 docs, 30 img"│
    │                                                      │
    │  verification: {passed: True, expected: ..., ...}    │
    │                                                      │
    │  retry_count: 0                                      │
    │  final_report: ""                                    │
    │  status: "executing"                                 │
    │                                                      │
    │  messages: [HumanMessage, AIMessage, ...]            │
    │  ↑ This stores the full conversation history         │
    │    for the LLM's context window                      │
    └──────────────────────────────────────────────────────┘
    """
    
    # ─── User Input ──────────────────────────────────────
    user_request: str               # The original task from the user
    
    # ─── Planning ────────────────────────────────────────
    plan: list[TaskStep]            # The execution plan (list of steps)
    current_step: int               # Index of the step currently being executed
    
    # ─── Execution ───────────────────────────────────────
    execution_result: str           # Output from the most recent tool execution
    
    # ─── Verification ────────────────────────────────────
    verification: VerificationResult  # Result of the verifier's check
    
    # ─── Recovery ────────────────────────────────────────
    retry_count: int                # How many times we've retried the current step
    error_message: str              # The error that caused a failure
    
    # ─── Output ──────────────────────────────────────────
    final_report: str               # The compiled final report for the user
    status: str                     # "planning" | "executing" | "verifying" | 
                                    # "recovering" | "completed" | "failed"
    
    # ─── LLM Conversation History ────────────────────────
    # This uses LangGraph's `add_messages` annotation which
    # APPENDS new messages instead of replacing them.
    # This is how the LLM "remembers" the conversation.
    messages: Annotated[list[BaseMessage], add_messages]
