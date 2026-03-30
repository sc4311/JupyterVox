from . import gemini_interface
from . import llama_cpp_interface


def get_ai_interface(client_name=None):
    """
    Return the appropriate AI backend module based on *client_name*.

    Parameters
    ----------
    client_name : str or None
        ``"gemini"`` or ``"ollama"`` (the default).

    Returns
    -------
    module
        A module that exposes at least ``generate(prompt, **kwargs)``.
    """
    if client_name == "gemini":
        return gemini_interface
    # Default to the Ollama / llama.cpp backend
    return llama_cpp_interface