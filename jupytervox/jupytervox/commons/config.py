#
# Parsing the configuration file for JVox server components, e.g., JupyterLab server extension, IPython extension.
#

import os
import tomllib
import sys

# add a default config to put all log files to /tmp if no config file is found, to avoid errors when logging without a config file
default_config = {
    "logs": {
        "ipython": "/tmp/jvox_ipython.log",
        "general": "/tmp/jvox_general.log",
        "JupyterLab": "/tmp/jvox_jupyterlab.log"
    }
}

def jvox_parse_config(config_path):
    """
    Reads all configuration entries from a TOML file and returns them as a dictionary.
    
    Parameters
    ----------
    config_path : str
        The path to the TOML configuration file.
    
    Returns
    -------
    dict
        Dictionary containing all configuration items.
    """

    if not isinstance(config_path, str):
        raise ValueError("Expected config_path to be a file path string")
    
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"TOML configuration file does not exist: {config_path}")
    
    with open(config_path, 'rb') as f:
        config = tomllib.load(f)
    return config


def jvox_load_config():
    """
    Loads configuration from the TOML file specified by the JVOX_CONFIG_FILE environment variable,
    or defaults to 'jvox_config.toml' in the current working directory if the environment variable is not set.

    Returns
    -------
    dict
        Configuration dictionary loaded from the TOML file.

    Raises
    ------
    FileNotFoundError
        If the specified TOML file does not exist.
    """
    global default_config

    config_path = os.environ.get("JVOX_CONFIG_FILE")
    if not config_path:
        # Default to 'jvox_config.toml' in the current working directory.
        config_path = os.path.join(os.getcwd(), "jvox_config.toml")

    if not os.path.isfile(config_path):
        # no config file found, return default config
        # not sure how to log this only to server console without logging to 
        # the notebook, so no logging at all
        # print(f"TOML configuration file does not exist: {config_path}", file=sys.__stderr__)
        #os.write(2, f"TOML configuration file does not exist: {config_path}\n".encode())
        return default_config
   
    return jvox_parse_config(config_path)


def jvox_ipython_log_path():
    """
    Return the log path for JVox's IPython extension 
    """

    config = jvox_load_config()

    log_path = config["logs"]["ipython"]

    return log_path

def jvox_general_log_path():
    """
    Return the log path for JVox's general logging
    """

    config = jvox_load_config()

    log_path = config["logs"]["general"]

    return log_path

def jvox_jupyterlab_log_path():
    """
    Return the log path for JVox's JupyterLab logging
    """

    config = jvox_load_config()

    log_path = config["logs"]["JupyterLab"]

    return log_path

if __name__ == "__main__":
    # Just call the one you want here
    config = jvox_load_config()
    print(f"Configurations:\n {config}")

    print(jvox_ipython_log_path())