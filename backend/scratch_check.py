import sys
import importlib.util

pkg = importlib.util.find_spec('langgraph.checkpoint.postgres')
print("Postgres Saver installed:", pkg is not None)
