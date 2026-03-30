"""
JVox AI Settings Comm Extension

An IPython extension that receives AI backend settings (ai_client, api_key)
from the JupyterLab frontend via a Comm channel, so the %%jvoxAI cell magic
can use the user-chosen AI backend.

Usage:
    Loaded automatically by the JupyterLab frontend via:
        %load_ext jvox_ai_magics.jvox_ai_settings_comm
"""

import sys

# Current AI settings, shared with jvox_ai_magics
_ai_client = "ollama"
_api_key = ""

# The Comm object for receiving settings from the frontend
_jvox_ai_settings_comm = None


def get_ai_client():
    """Return the current AI client name ('ollama' or 'gemini')."""
    return _ai_client


def get_api_key():
    """Return the current API key (may be empty)."""
    return _api_key


def _jvox_ai_settings_comm_msg(comm, open_msg):
    """Called when the frontend opens the 'jvox_ai_settings' Comm channel."""
    global _jvox_ai_settings_comm
    _jvox_ai_settings_comm = comm

    # Process any initial data sent with the open message
    if open_msg.get("content", {}).get("data"):
        _apply_settings(open_msg["content"]["data"])

    # Handle subsequent messages
    @comm.on_msg
    def _on_msg(msg):
        _apply_settings(msg["content"]["data"])

    @comm.on_close
    def _on_close(msg):
        global _jvox_ai_settings_comm
        _jvox_ai_settings_comm = None


def _apply_settings(data):
    """Apply AI settings received from the frontend."""
    global _ai_client, _api_key

    if "ai_client" in data:
        _ai_client = data["ai_client"]
    if "api_key" in data:
        _api_key = data["api_key"]

    print(
        f"JVox AI settings updated – client: {_ai_client}, "
        f"api_key: {'(set)' if _api_key else '(empty)'}",
        file=sys.stderr,
    )


def load_ipython_extension(ipython):
    """Register the Comm target when loaded via %load_ext."""
    ipython.kernel.comm_manager.register_target(
        "jvox_ai_settings", _jvox_ai_settings_comm_msg
    )


def unload_ipython_extension(ipython):
    """Unregister the extension."""
    global _jvox_ai_settings_comm
    if _jvox_ai_settings_comm is not None:
        try:
            _jvox_ai_settings_comm.close()
        except Exception:
            pass
        _jvox_ai_settings_comm = None
