"""
Chat route — the frontend sends a natural-language message and gets back
structured actions (log / edit / lookup) plus an AI response.
Tools do the real DB work; this route just orchestrates.
"""

import uuid
import json
import asyncio
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from app.models.users import User
from app.schemas.chat import ChatRequest
from app.dependencies.auth import get_current_user
from app.agent.graph import get_agent

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        agent = get_agent()

        # Inject today's date into the message for context
        today = date.today().isoformat()
        enriched_message = f"[Today's date is {today}] [User ID: {current_user.id}] {body.message}"

        # Use a thread_id for conversation continuity
        thread_id = body.thread_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        # ── Snapshot existing message count so we only parse NEW messages ──
        # With a checkpointer, result["messages"] returns the FULL history.
        existing_count = 0
        try:
            snapshot = await asyncio.to_thread(agent.get_state, config)
            if snapshot and snapshot.values and "messages" in snapshot.values:
                existing_count = len(snapshot.values["messages"])
        except Exception:
            existing_count = 0  # first turn — no prior state

        # Invoke the LangGraph agent with explicit state (sync call → run in thread pool)
        result = await asyncio.to_thread(
            agent.invoke,
            {
                "messages": [HumanMessage(content=enriched_message)],
                "user_id": current_user.id,
                "interaction_id": body.current_interaction_id,
            },
            config,
        )

        # ── Only process messages from THIS turn ──
        all_messages = result.get("messages", [])
        new_messages = all_messages[existing_count:]

        ai_text = ""
        actions = []

        for msg in new_messages:
            # Collect tool call results (real DB results from tools)
            if isinstance(msg, ToolMessage):
                try:
                    tool_result = (
                        json.loads(msg.content)
                        if isinstance(msg.content, str)
                        else msg.content
                    )
                    if isinstance(tool_result, dict) and "action" in tool_result:
                        actions.append(tool_result)
                except (json.JSONDecodeError, TypeError):
                    pass

            # Collect final AI text response
            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                ai_text = msg.content

        return {
            "success": True,
            "thread_id": thread_id,
            "response": ai_text,
            "actions": actions,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent error: {str(e)}",
        )
