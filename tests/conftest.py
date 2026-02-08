import sys
import os

# Add api/ and mcp/ to sys.path so tests can import modules directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp"))
