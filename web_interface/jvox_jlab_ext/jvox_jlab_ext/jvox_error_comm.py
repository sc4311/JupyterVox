"""
JVox Kernel Error Comm Extension

An IPython extension that intercepts cell execution errors and sends
structured error information (type, message, line, column) to the
JupyterLab frontend via a Comm channel.

Usage:
    Load in a notebook with: %load_ext jvox_jlab_ext.jvox_error_comm
    Or auto-load by adding to IPython config.
"""

import traceback
import sys

# The Comm object for sending error data to the frontend
_jvox_error_comm = None


def _jvox_post_run_cell(result):
    """
    Called by IPython after every cell execution.
    If an error occurred, extract structured error info and send it
    to the frontend via the Comm channel.

    Args:
        result: IPython's ExecutionResult object, which has:
            - error_before_exec: exception raised before execution (e.g., SyntaxError)
            - error_in_exec: exception raised during execution (e.g., TypeError)
    """
    global _jvox_error_comm
    if _jvox_error_comm is None:
        return

    error = result.error_before_exec or result.error_in_exec
    if error is None:
        return

    error_data = {
        'type': type(error).__name__,
        'message': str(error),
        'line': -1,
        'column': -1,
        'end_line': -1,
        'end_column': -1,
        'text': '',
    }

    if isinstance(error, SyntaxError):
        # SyntaxError has structured location fields
        if error.lineno is not None:
            error_data['line'] = error.lineno           # 1-based
        if error.offset is not None:
            error_data['column'] = error.offset          # 1-based
        # end_lineno and end_offset available in Python 3.10+
        if hasattr(error, 'end_lineno') and error.end_lineno is not None:
            error_data['end_line'] = error.end_lineno    # 1-based
        if hasattr(error, 'end_offset') and error.end_offset is not None:
            error_data['end_column'] = error.end_offset  # 1-based
        if error.text is not None:
            error_data['text'] = error.text
    else:
        # For runtime errors, extract location from the traceback
        tb = error.__traceback__
        if tb:
            frames = traceback.extract_tb(tb)
            if frames:
                # The last frame is the actual error location
                last_frame = frames[-1]
                error_data['line'] = last_frame.lineno   # 1-based
                error_data['text'] = last_frame.line or ''

                # colno and end_colno available in Python 3.11+
                if hasattr(last_frame, 'colno') and last_frame.colno is not None:
                    error_data['column'] = last_frame.colno + 1        # convert 0-based to 1-based
                if hasattr(last_frame, 'end_colno') and last_frame.end_colno is not None:
                    error_data['end_column'] = last_frame.end_colno + 1  # convert 0-based to 1-based

    try:
        _jvox_error_comm.send(data=error_data)
    except Exception as e:
        print(f"JVox: Failed to send error data via comm: {e}", file=sys.stderr)


def _jvox_comm_open(comm, open_msg):
    """Called when the frontend opens the 'jvox_error_info' Comm channel."""
    global _jvox_error_comm
    _jvox_error_comm = comm

    # Handle comm close from frontend
    @comm.on_close
    def _on_close(msg):
        global _jvox_error_comm
        _jvox_error_comm = None


def load_ipython_extension(ipython):
    """Register the extension when loaded via %load_ext."""
    ipython.events.register('post_run_cell', _jvox_post_run_cell)
    ipython.kernel.comm_manager.register_target(
        'jvox_error_info', _jvox_comm_open
    )


def unload_ipython_extension(ipython):
    """Unregister the extension."""
    global _jvox_error_comm
    try:
        ipython.events.unregister('post_run_cell', _jvox_post_run_cell)
    except ValueError:
        pass
    _jvox_error_comm = None
