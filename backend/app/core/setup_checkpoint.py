# setup_checkpoint.py
from psycopg import connect
from langgraph.checkpoint.postgres import PostgresSaver
from app.core.config import settings

conn = connect(settings.database_url)
conn.autocommit = True  # ✅ critical

checkpointer = PostgresSaver(conn)
checkpointer.setup()

conn.close()