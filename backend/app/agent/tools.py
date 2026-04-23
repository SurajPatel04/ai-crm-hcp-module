"""
LangGraph Agent Tools for HCP Interaction Management.

Five tools with REAL database operations:
1. log_interaction         — INSERT new interaction into DB + populate form
2. edit_interaction        — UPDATE specific fields in DB + update form
3. get_hcp_info            — SELECT HCP profile from DB
4. list_past_interactions  — SELECT past interactions from DB
5. suggest_followup        — SELECT last interaction + return context for AI recommendations
"""

import json
import re
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState
from typing import Optional, Annotated, List
from datetime import date, datetime, time
from sqlalchemy import select, update as sql_update, or_

from app.core.database import SyncSessionLocal
from app.core.config import settings
from app.models.interaction import Interaction, InteractionType, SentimentType
from app.models.hcp import HCP

# Helper
def _parse_date(date_str: str) -> date:
    """Parse YYYY-MM-DD string to date object."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return date.today()


def _parse_time(time_str: Optional[str]) -> Optional[time]:
    """Parse HH:MM or HH:MM:SS string to time object."""
    if not time_str:
        return None
    try:
        if len(time_str) == 5:
            return datetime.strptime(time_str, "%H:%M").time()
        return datetime.strptime(time_str, "%H:%M:%S").time()
    except (ValueError, TypeError):
        return None


def _map_interaction_type(type_str: str) -> InteractionType:
    """Map string to InteractionType enum."""
    mapping = {
        "meeting": InteractionType.meeting,
        "call": InteractionType.call,
        "email": InteractionType.email,
        "conference": InteractionType.conference,
        "virtual": InteractionType.virtual,
    }
    return mapping.get(type_str.lower(), InteractionType.meeting)


def _map_sentiment(sentiment_str: str) -> SentimentType:
    """Map string to SentimentType enum."""
    mapping = {
        "positive": SentimentType.positive,
        "neutral": SentimentType.neutral,
        "negative": SentimentType.negative,
    }
    return mapping.get(sentiment_str.lower(), SentimentType.neutral)


def _get_or_create_hcp(db, hcp_name: str) -> HCP:
    """Find an HCP by name, or create a new record."""
    hcp = db.execute(
        select(HCP).where(HCP.full_name.ilike(f"%{hcp_name}%"))
    ).scalar_one_or_none()

    if not hcp:
        hcp = HCP(full_name=hcp_name)
        db.add(hcp)
        db.flush()

    return hcp


#Tool 1: Log Interaction (mandatory)
@tool
def log_interaction(
    hcp_name: str,
    interaction_date: str,
    interaction_type: str = "Meeting",
    interaction_time: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    sentiment: str = "Neutral",
    outcomes: Optional[str] = None,
    ai_summary: Optional[str] = None,
    user_id: Annotated[int, InjectedState("user_id")] = None,
) -> dict:
    """
    Log a new HCP interaction into the database. Extracts structured data
    from the user's natural-language description, inserts it into PostgreSQL,
    and returns form data for the UI.

    Args:
        hcp_name: Full name of the Healthcare Professional (e.g. "Dr. Smith").
        interaction_date: Date in YYYY-MM-DD format. Use today's date if user says "today".
        interaction_type: One of Meeting, Call, Email, Conference, Virtual.
        interaction_time: Time in HH:MM format (24-hour). Optional.
        topics_discussed: Summary of topics discussed.
        sentiment: One of Positive, Neutral, Negative.
        outcomes: Key outcomes or next steps.
        ai_summary: A concise AI-generated summary of the interaction.

    Returns:
        Dictionary with action type, DB interaction_id, and form_data for the UI.
    """
    db = SyncSessionLocal()
    try:
        hcp = _get_or_create_hcp(db, hcp_name)

        new_interaction = Interaction(
            hcp_id=hcp.id,
            logged_by_user_id=user_id,
            interaction_type=_map_interaction_type(interaction_type),
            interaction_date=_parse_date(interaction_date),
            interaction_time=_parse_time(interaction_time),
            topics_discussed=topics_discussed,
            sentiment=_map_sentiment(sentiment),
            outcomes=outcomes,
            ai_summary=ai_summary,
            log_method="chat",
        )
        db.add(new_interaction)
        db.commit()
        db.refresh(new_interaction)

        return {
            "action": "log_interaction",
            "interaction_id": new_interaction.id,
            "form_data": {
                "hcp_name": hcp.full_name,
                "hcp_id": hcp.id,
                "interaction_date": str(new_interaction.interaction_date),
                "interaction_type": interaction_type,
                "interaction_time": interaction_time,
                "topics_discussed": topics_discussed,
                "sentiment": sentiment,
                "outcomes": outcomes,
                "ai_summary": ai_summary,
            },
            "message": f"Interaction with {hcp.full_name} saved to database (ID: {new_interaction.id}).",
        }

    except Exception as e:
        db.rollback()
        return {"action": "log_interaction", "error": str(e)}
    finally:
        db.close()


#Tool 2: Edit Interaction (mandatory)
@tool
def edit_interaction(
    hcp_name: Optional[str] = None,
    interaction_date: Optional[str] = None,
    interaction_type: Optional[str] = None,
    interaction_time: Optional[str] = None,
    topics_discussed: Optional[str] = None,
    sentiment: Optional[str] = None,
    outcomes: Optional[str] = None,
    ai_summary: Optional[str] = None,
    interaction_id: Annotated[Optional[int], InjectedState("interaction_id")] = None,
) -> dict:
    """
    Edit specific fields of the most recently logged interaction in the database.
    Only provide the fields that need to be changed — all other fields stay as-is.

    Args:
        hcp_name: Updated HCP name, if it needs to change.
        interaction_date: Updated date in YYYY-MM-DD, if it needs to change.
        interaction_type: Updated type (Meeting/Call/Email/Conference/Virtual).
        interaction_time: Updated time in HH:MM format.
        topics_discussed: Updated topics.
        sentiment: Updated sentiment (Positive/Neutral/Negative).
        outcomes: Updated outcomes.
        ai_summary: Updated AI summary.

    Returns:
        Dictionary with action type and only the changed fields.
    """
    db = SyncSessionLocal()
    try:
        if not interaction_id:
            return {
                "action": "edit_interaction",
                "error": "No interaction is currently loaded. Please log an interaction first.",
            }

        interaction = db.execute(
            select(Interaction).where(Interaction.id == interaction_id)
        ).scalar_one_or_none()

        if not interaction:
            return {
                "action": "edit_interaction",
                "error": f"Interaction ID {interaction_id} not found in database.",
            }

        updated_fields = {}

        if hcp_name is not None:
            hcp = _get_or_create_hcp(db, hcp_name)
            interaction.hcp_id = hcp.id
            updated_fields["hcp_name"] = hcp.full_name
            updated_fields["hcp_id"] = hcp.id

        if interaction_date is not None:
            interaction.interaction_date = _parse_date(interaction_date)
            updated_fields["interaction_date"] = interaction_date

        if interaction_type is not None:
            interaction.interaction_type = _map_interaction_type(interaction_type)
            updated_fields["interaction_type"] = interaction_type

        if interaction_time is not None:
            interaction.interaction_time = _parse_time(interaction_time)
            updated_fields["interaction_time"] = interaction_time

        if topics_discussed is not None:
            interaction.topics_discussed = topics_discussed
            updated_fields["topics_discussed"] = topics_discussed

        if sentiment is not None:
            interaction.sentiment = _map_sentiment(sentiment)
            updated_fields["sentiment"] = sentiment

        if outcomes is not None:
            interaction.outcomes = outcomes
            updated_fields["outcomes"] = outcomes

        if ai_summary is not None:
            interaction.ai_summary = ai_summary
            updated_fields["ai_summary"] = ai_summary

        db.commit()

        return {
            "action": "edit_interaction",
            "interaction_id": interaction_id,
            "form_data": updated_fields,
            "message": f"Updated fields: {', '.join(updated_fields.keys())} (ID: {interaction_id}).",
        }

    except Exception as e:
        db.rollback()
        return {"action": "edit_interaction", "error": str(e)}
    finally:
        db.close()


#  Tool 3: Get HCP Info
@tool
def get_hcp_info(hcp_name: str) -> dict:
    """
    Look up a Healthcare Professional by name in the database and return
    their full profile information.

    Args:
        hcp_name: Name (or partial name) of the HCP to search for.

    Returns:
        Dictionary with HCP profile data from the database.
    """
    db = SyncSessionLocal()
    try:
        hcp = db.execute(
            select(HCP).where(HCP.full_name.ilike(f"%{hcp_name}%"))
        ).scalar_one_or_none()

        if not hcp:
            return {
                "action": "get_hcp_info",
                "error": f"No HCP found matching '{hcp_name}'",
                "hcp_data": None,
            }

        return {
            "action": "get_hcp_info",
            "hcp_data": {
                "id": hcp.id,
                "full_name": hcp.full_name,
                "specialty": hcp.specialty.value if hcp.specialty else None,
                "institution": hcp.institution,
                "city": hcp.city,
                "email": hcp.email,
                "phone": hcp.phone,
                "created_at": str(hcp.created_at) if hcp.created_at else None,
            },
            "message": f"Found HCP: {hcp.full_name}",
        }

    except Exception as e:
        return {"action": "get_hcp_info", "error": str(e)}
    finally:
        db.close()


# ─── Tool 4: List Past Interactions ─────────────────────────────────
@tool
def list_past_interactions(hcp_name: str, limit: int = 5) -> dict:
    """
    Fetch past interactions for a specific HCP from the database so the user
    can review history before logging a new one.

    Args:
        hcp_name: Name of the HCP whose interaction history to fetch.
        limit: Maximum number of past interactions to return (default 5).

    Returns:
        Dictionary with list of past interactions from the database.
    """
    db = SyncSessionLocal()
    try:
        hcp = db.execute(
            select(HCP).where(HCP.full_name.ilike(f"%{hcp_name}%"))
        ).scalar_one_or_none()

        if not hcp:
            return {
                "action": "list_past_interactions",
                "interactions": [],
                "message": f"No HCP found matching '{hcp_name}'",
            }

        interactions = db.execute(
            select(Interaction)
            .where(Interaction.hcp_id == hcp.id)
            .order_by(Interaction.interaction_date.desc())
            .limit(limit)
        ).scalars().all()

        history = [
            {
                "id": i.id,
                "interaction_date": str(i.interaction_date) if i.interaction_date else None,
                "interaction_type": i.interaction_type.value if i.interaction_type else None,
                "topics_discussed": i.topics_discussed,
                "sentiment": i.sentiment.value if i.sentiment else None,
                "outcomes": i.outcomes,
                "ai_summary": i.ai_summary,
            }
            for i in interactions
        ]

        return {
            "action": "list_past_interactions",
            "hcp_name": hcp.full_name,
            "interactions": history,
            "message": f"Found {len(history)} past interactions with {hcp.full_name}",
        }

    except Exception as e:
        return {"action": "list_past_interactions", "error": str(e)}
    finally:
        db.close()


# ─── Tool 5: Suggest Follow-up ──────────────────────────────────────
@tool
def suggest_followup(hcp_name: str) -> dict:
    """
    Fetch the most recent interaction with an HCP from the database and return
    the context so the AI can generate smart follow-up recommendations for
    sales planning and relationship building.

    Args:
        hcp_name: Name of the HCP to generate follow-up suggestions for.

    Returns:
        Dictionary with last interaction context for AI-powered recommendations.
    """
    db = SyncSessionLocal()
    try:
        hcp = db.execute(
            select(HCP).where(HCP.full_name.ilike(f"%{hcp_name}%"))
        ).scalar_one_or_none()

        if not hcp:
            return {
                "action": "suggest_followup",
                "error": f"No HCP found matching '{hcp_name}'",
            }

        last_interaction = db.execute(
            select(Interaction)
            .where(Interaction.hcp_id == hcp.id)
            .order_by(Interaction.interaction_date.desc())
            .limit(1)
        ).scalar_one_or_none()

        if not last_interaction:
            return {
                "action": "suggest_followup",
                "hcp_name": hcp.full_name,
                "context": None,
                "message": f"No past interactions found with {hcp.full_name}. Consider scheduling an introductory meeting.",
            }

        return {
            "action": "suggest_followup",
            "hcp_name": hcp.full_name,
            "context": {
                "last_date": str(last_interaction.interaction_date) if last_interaction.interaction_date else None,
                "last_type": last_interaction.interaction_type.value if last_interaction.interaction_type else None,
                "last_topics": last_interaction.topics_discussed,
                "last_sentiment": last_interaction.sentiment.value if last_interaction.sentiment else None,
                "last_outcomes": last_interaction.outcomes,
                "last_summary": last_interaction.ai_summary,
            },
            "message": f"Retrieved context for {hcp.full_name}. Generating follow-up suggestions...",
        }

    except Exception as e:
        return {"action": "suggest_followup", "error": str(e)}
    finally:
        db.close()


# ─── Tool 6: Extract HCP From Context ───────────────────────────────
@tool
def extract_hcp_from_context(conversation_text: str) -> dict:
    """
    Uses LLM to extract a Healthcare Professional (HCP / doctor) name from
    free-form conversation text.  If no name is found, returns a flag
    indicating the agent should ask the user for clarification.

    Args:
        conversation_text: The user's raw message or conversation text to
                          parse for an HCP name.

    Returns:
        Dictionary with extracted hcp_name (or null) and needs_clarification flag.
    """
    try:
        from groq import Groq
    except ImportError:
        return {
            "action": "extract_hcp_from_context",
            "error": "groq package not installed",
            "hcp_name": None,
            "needs_clarification": True,
        }

    prompt = f"""Extract the HCP (doctor/healthcare professional) name from this text.
If no name is found, return {{"hcp_name": null, "needs_clarification": true}}.
If a name IS found, return {{"hcp_name": "<name>", "needs_clarification": false}}.

Text: {conversation_text}

Return JSON only — no markdown, no explanation."""

    try:
        groq_client = Groq(api_key=settings.groq_api_key)
        response = groq_client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)

        parsed = json.loads(raw)

        hcp_name = parsed.get("hcp_name")
        needs_clarification = parsed.get("needs_clarification", hcp_name is None)

        result = {
            "action": "extract_hcp_from_context",
            "hcp_name": hcp_name,
            "needs_clarification": needs_clarification,
        }

        # If a name was found, try to fuzzy-match in DB
        if hcp_name:
            db = SyncSessionLocal()
            try:
                hcp = db.execute(
                    select(HCP).where(HCP.full_name.ilike(f"%{hcp_name}%"))
                ).scalar_one_or_none()
                if hcp:
                    result["matched_hcp"] = {
                        "id": hcp.id,
                        "full_name": hcp.full_name,
                        "specialty": hcp.specialty.value if hcp.specialty else None,
                        "institution": hcp.institution,
                        "city": hcp.city,
                    }
                    result["message"] = f"Matched HCP: {hcp.full_name} (ID: {hcp.id})"
                else:
                    result["matched_hcp"] = None
                    result["message"] = f"Name '{hcp_name}' extracted but no match in database."
            finally:
                db.close()

        return result

    except Exception as e:
        return {
            "action": "extract_hcp_from_context",
            "error": str(e),
            "hcp_name": None,
            "needs_clarification": True,
        }


# ─── Tool 7: Search HCP Database ────────────────────────────────────
@tool
def search_hcp_database(
    query: Optional[str] = None,
    specialty: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = 10,
) -> dict:
    """
    Search the HCP database by name, specialty, or city.  Useful when the
    user provides partial information (e.g. "a cardiologist in Mumbai") and
    the agent needs to find matching doctors.

    Args:
        query: Free-text search term matched against HCP name and institution.
        specialty: Filter by specialty (e.g. Cardiologist, Oncologist).
        city: Filter by city (e.g. Mumbai, Bengaluru).
        limit: Maximum results to return (default 10).

    Returns:
        Dictionary with a list of matching HCPs from the database.
    """
    db = SyncSessionLocal()
    try:
        stmt = select(HCP)
        filters = []

        if query:
            pattern = f"%{query}%"
            filters.append(
                or_(HCP.full_name.ilike(pattern), HCP.institution.ilike(pattern))
            )

        if specialty:
            filters.append(HCP.specialty == specialty.lower())

        if city:
            filters.append(HCP.city.ilike(f"%{city}%"))

        if filters:
            stmt = stmt.where(*filters)

        stmt = stmt.order_by(HCP.full_name).limit(limit)
        results = db.execute(stmt).scalars().all()

        matches = [
            {
                "id": h.id,
                "full_name": h.full_name,
                "specialty": h.specialty.value if h.specialty else None,
                "institution": h.institution,
                "city": h.city,
                "email": h.email,
                "phone": h.phone,
            }
            for h in results
        ]

        return {
            "action": "search_hcp_database",
            "matches": matches,
            "total": len(matches),
            "message": f"Found {len(matches)} HCP(s) matching your criteria.",
        }

    except Exception as e:
        return {"action": "search_hcp_database", "error": str(e), "matches": []}
    finally:
        db.close()


# ─── Export ──────────────────────────────────────────────────────────
all_tools = [
    log_interaction,
    edit_interaction,
    get_hcp_info,
    list_past_interactions,
    suggest_followup,
    extract_hcp_from_context,
    search_hcp_database,
]
