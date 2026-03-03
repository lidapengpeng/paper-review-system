"""Shared test configuration — adds MCP server source dirs to sys.path."""
import sys
import os

_root = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(_root, "academic-search-mcp"))
sys.path.insert(0, os.path.join(_root, "paper-parser-mcp"))
