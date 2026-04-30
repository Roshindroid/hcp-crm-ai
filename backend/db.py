import os
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")


def _connect():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    """Create the interactions table if it doesn't exist."""
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id SERIAL PRIMARY KEY,
                hcp_name TEXT,
                date DATE,
                interaction_type TEXT,
                attendees TEXT,
                topics TEXT,
                sentiment TEXT,
                materials_shared BOOLEAN,
                summary TEXT,
                raw_input TEXT,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        conn.commit()


def save_interaction(state: dict) -> int:
    """Persist a completed interaction. Returns the new row id."""
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO interactions
                (hcp_name, date, interaction_type, attendees, topics,
                 sentiment, materials_shared, summary, raw_input)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                state.get("hcp_name"),
                state.get("date"),
                state.get("interaction_type"),
                state.get("attendees"),
                state.get("topics"),
                state.get("sentiment"),
                state.get("materials_shared"),
                state.get("summary"),
                state.get("input"),
            ),
        )
        row = cur.fetchone()
        conn.commit()
        return row["id"] if row else -1


def list_interactions(limit: int = 50):
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT id, hcp_name, date, interaction_type, attendees, topics,
                   sentiment, materials_shared, summary, created_at
            FROM interactions
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
        for r in rows:
            if r.get("date") is not None:
                r["date"] = r["date"].isoformat()
            if r.get("created_at") is not None:
                r["created_at"] = r["created_at"].isoformat()
        return rows
