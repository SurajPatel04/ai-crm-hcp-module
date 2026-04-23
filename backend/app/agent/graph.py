from langgraph.prebuilt import create_react_agent
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage
from langgraph.prebuilt.chat_agent_executor import AgentState as BaseAgentState
from app.agent.tools import all_tools
from app.core.config import settings
from typing import Optional

try:
    from psycopg_pool import ConnectionPool
    from langgraph.checkpoint.postgres import PostgresSaver
except ImportError:
    ConnectionPool = None
    PostgresSaver = None



class AgentState(BaseAgentState):
    user_id: Optional[int]
    interaction_id: Optional[int]

_agent = None


SYSTEM_PROMPT = """You are an AI assistant for a Healthcare CRM system used by pharmaceutical field representatives.

Your role is to help users log and manage interactions with Healthcare Professionals (HCPs).

You have access to the following tools:
1. **log_interaction** — Use when the user describes a new interaction. Extract ALL relevant 
   fields (HCP name, date, type, time, topics, sentiment, outcomes) from their message and 
   call this tool to populate the form. If the user says "today", use the current date. 
   Always generate an ai_summary.
2. **edit_interaction** — Use when the user wants to correct or update specific fields in 
   the currently displayed form. Only pass the fields that need to change.
3. **get_hcp_info** — Use when the user asks about a specific HCP's profile or details.
4. **list_past_interactions** — Use when the user wants to see previous interactions with an HCP.
5. **suggest_followup** — Use when the user asks for follow-up recommendations or 
   next steps after an interaction.
6. **extract_hcp_from_context** — Use when the user describes an interaction but does NOT 
   mention a doctor/HCP name. This tool uses AI to attempt extracting the name from free-form text.
7. **search_hcp_database** — Use to search registered HCPs by name, specialty, or city. 
   Helpful when you need to find or suggest matching doctors from the database.

CRITICAL — Handling Missing HCP Names:
When a user describes an interaction without mentioning which doctor they met:
1. First, call extract_hcp_from_context with their message to try extracting any doctor name.
2. If no name is found (needs_clarification = true), check if they mentioned a specialty or 
   location, then call search_hcp_database to find potential matches.
3. Respond helpfully: "I'd love to log that! Could you tell me which doctor you met with? 
   You can say their name or I can search our database." If you found potential matches from 
   the search, suggest them: "Based on the specialty/location you mentioned, could it be 
   one of these: [list matches]?"
4. Once the user provides or confirms the HCP name, proceed to log the interaction normally.
5. NEVER log an interaction without an HCP name — always clarify first.

Important rules:
- When logging an interaction, ALWAYS use the log_interaction tool — do NOT just respond with text.
- When the user corrects a field, use edit_interaction with ONLY the changed fields.
- For dates: if the user says "today", use today's date in YYYY-MM-DD format.
- For sentiment: map the user's language to Positive, Neutral, or Negative.
- For interaction_type: map to one of Meeting, Call, Email, Conference, or Virtual.
- Always confirm what you've done after calling a tool.
- Generate a concise ai_summary whenever logging or editing interactions.
- If the user greets you (hello, hi, hey), respond warmly and ask how you can help 
  with their HCP interactions today. Do NOT call any tool for greetings.
- If the user asks to edit/change something but no interaction is currently loaded 
  (interaction_id is None), ask them to first describe the interaction or specify 
  which HCP and date to look up — do NOT call edit_interaction.
"""


def get_agent():
    """Return the compiled LangGraph agent, creating it on first call."""
    global _agent
    if _agent is not None:
        return _agent

    try:
        from langchain_groq import ChatGroq
    except ImportError:
        raise ImportError(
            "langchain-groq is required. Install it with: pip install langchain-groq"
        )

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=settings.groq_api_key,
        temperature=0,
    )

    if PostgresSaver is None:
        raise ImportError(
            "langgraph-checkpoint-postgres and psycopg_pool are required for the checkpointer. "
            "Install with: pip install langgraph-checkpoint-postgres psycopg-pool psycopg[binary]"
        )

    from psycopg import connect
    with connect(settings.database_url, autocommit=True) as setup_conn:
        PostgresSaver(setup_conn).setup()

    pool = ConnectionPool(conninfo=settings.database_url)
    checkpointer = PostgresSaver(pool)

    _agent = create_react_agent(
        model=llm,
        tools=all_tools,
        prompt=SystemMessage(content=SYSTEM_PROMPT),
        state_schema=AgentState,
        checkpointer=checkpointer,
    )

    return _agent
