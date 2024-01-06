# Server Configuration
## 1. VM Creation
1. One Lightsail VM with 2 vcpu and 512MB
2. Add a network rule to allow port 8888
## 2. Jupyter Notebook Installation
1. Install Python packages
> sudo apt install python3 python3-dev python3-venv python3-pip
2. Create the virtual environment
> python3 -m venv ~/JupyterVox/python_env/
3. Enter the virtual environment
> source ~/JupyterVox/python_env/bin/activate
4. Create a configuration file, so that we can change the base_url/directory for Apache reverse proxy
> jupyter notebook --generate-config
5. In ~/.jupyter/jupyter_notebook_config.py, change c.NotebookApp.base_url to "ipython"
> c.NotebookApp.base_url = '/ipython'
4. Install Jupyter Notebook. For nbextensions to work, we need to install a special version of it,
> pip3 install --upgrade notebook==6.4.12
5. All need to install a special version of traitlets
> pip3 uninstall traitlets
> pip3 install traitlets==5.9.0
6. The above are from https://stackoverflow.com/q/76893872
7. Start Jupyter Notebook
> jupyter notebook --no-mathjax --no-browser --ip 0.0.0.0 --port 8888
8. Test the connection to jupyter notebook in a browser, the address should be http://*publicip*:8888/ipython. The access token is shown in the shell output
## 3. Notebook extensions Installation
1. Based on https://jupyter-contrib-nbextensions.readthedocs.io/en/latest/install.html
2. Make sure we are in the JVox Python environment
> source ~/JupyterVox/python_env/bin/activate
3. Install the extensions with pip
> pip3 install jupyter_contrib_nbextensions 
4. Enable the extenions in JupyterNote book
> jupyter contrib nbextension install --user
5. Start Jupyter Notebook. See Section 2.7 and 2.8
6. Test if the extension works or not. See https://towardsdatascience.com/jupyter-notebook-extensions-517fa69d2231. Ignore compactibility. I tested with the VarInspector extension, although I can only see the extension the window, not the variables.
## 4. Install and configure Apache
1. Install Apache
> sudo apt install apache2
2. Enable modules
> sudo a2enmod
3. Enable these mods: proxy proxy_http proxy_https proxy_wstunnel ssl headers. Note, seems proxy_https does not exist?
4. Restart Apache
> systemctl restart apache2
5. Test if the server works with a browser, http://*publicip*. Assuming port 80 is open. 
## 5. Apache reverse proxy for Jupyter Notebook
1. based on
    1. https://www.linode.com/docs/guides/install-a-jupyter-notebook-server-on-a-linode-behind-an-apache-reverse-proxy/
    2. https://stackoverflow.com/questions/23890386/how-to-run-ipython-behind-an-apache-proxy
2. In /etc/apache2/sites-available, create a configuration for Jupyter Notebook and jvox
> sudo cp 000-default.conf jvox.conf
3. In jvox.conf, in the virtual host section, add the following. Note change publicip to VM's public ip
    <Location /ipython>
	ProxyPass        http://localhost:8888/ipython
	ProxyPassReverse http://localhost:8888/ipython
	ProxyPassReverseCookieDomain localhost *publicip*
	RequestHeader set Origin "http://localhost:8888"
	</Location>

	<Location /ipython/api/kernels/>
	ProxyPass        ws://localhost:8888/ipython/api/kernels/
	ProxyPassReverse ws://localhost:8888/ipython/api/kernels/
	</Location>
4. Test. Access through http://*publicip*/ipython. The access is very slow for me. I don't know why. SOmetimes I had to use the "stop" button in the browser to get things displayed, or had to wait for quite a few minutes (5 min?)

## 6. Setup Web Service
1. Clone code to a new directory
> git clone https://github.com/ProgrammingEduBVI/JupyterVox.git
2. Enter JVox Python environment, install flask and gtts with pip
3. Go to the web_api directory of our code, run test_service.py
> python3 test_service.py
4. Test the service
    1. Pure text return, command: curl --header "Content-Type: application/json"   --request POST   --data '{"stmt":"a = b*c"}'   http://localhost:5000/speech2/post
    2. mp3 generation, curl --header "Content-Type: application/json"   --request POST   --data '{"stmt":"a = b*c+12"}'   http://localhost:5000/speech3/post --output /tmp/test.mp3
5. Add the following lines to Apache's jvox.conf to forward http requests to our web service,
    <Location /jvox/speech2/post>
	ProxyPass        http://localhost:5000/speech2/post
	ProxyPassReverse http://localhost:5000/speech2/post
	</Location>

	<Location /jvox/speech3/post>
	ProxyPass        http://localhost:5000/speech3/post
	ProxyPassReverse http://localhost:5000/speech3/post
	</Location>
6. Test with the following command remotely,
    1. curl --header "Content-Type: application/json"   --request POST   --data '{"stmt":"a = b*c"}'   http://*publicip*/jvox/speech2/post
    2. curl --header "Content-Type: application/json"   --request POST   --data '{"stmt":"a = b*c+12"}'   http://*publicip*/jvox/speech3/post --output /tmp/test.mp3
    3. The frist one should reply the statment, the second one should return a valid mp3 with statement reading.

## 7. Set up the JVox notebook extension
1. Make sure JVOx code is cloned and JVox Python environment is enter
2. Make sure Jupyter notebook, JVox web service, and Apache are both running
3. Modify the JS code with the correct API. In our code, file notebook_extension/jvox_ext/main.js, function "http_post_speech_with_mp3", change surl to the correct URL, "http://*publicip*/jvox/speech3/post"
4. Install and enable the extension, in our code, direcotry notebook_extension/
    1. Install: jupyter nbextension install jvox_ext --user
    2. Enable: jupyter nbextension enable jvox_ext/main --user
5. Final test, go to http://*publicip*/ipython, create a new notebook, create a cell, write a simple expression (e.g., a = 11 + 13), put cursor in the on this line, use the "paper plane" button on the tool bar or "alt+n" to listen to the screen reading. 
6. If not working, check browser's JS console (from developer tools), and do the tests from the above steps. 

## 8. Antlr4 Setup
1. This is required for the new and current antlr4 parser based JVox. 
2. Based on https://stackoverflow.com/q/63128280
3. pip3 install antlr4-tools
    1. outputs: Collecting antlr4-tools
  Downloading antlr4_tools-0.2.1-py3-none-any.whl (4.3 kB)
Collecting install-jdk
  Downloading install_jdk-1.1.0-py3-none-any.whl (15 kB)
Installing collected packages: install-jdk, antlr4-tools
Successfully installed antlr4-tools-0.2.1 install-jdk-1.1.0

4. antlr4:
    1. output: Downloading antlr4-4.13.1-complete.jar
ANTLR tool needs Java to run; install Java JRE 11 yes/no (default yes)? yes
Installed Java in /home/admin/.jre/jdk-11.0.21+9-jre; remove that dir to uninstall
ANTLR Parser Generator  Version 4.13.1
 -o ___              specify output directory where all output is generated
 -lib ___            specify location of grammars, tokens files
 -atn                generate rule augmented transition network diagrams
 -encoding ___       specify grammar file encoding; e.g., euc-jp
 -message-format ___ specify output style for messages in antlr, gnu, vs2005
 -long-messages      show exception details when available for errors and warnings
 -listener           generate parse tree listener (default)
 -no-listener        don't generate parse tree listener
 -visitor            generate parse tree visitor
 -no-visitor         don't generate parse tree visitor (default)
 -package ___        specify a package/namespace for the generated code
 -depend             generate file dependencies
 -D<option>=value    set/override a grammar-level option
 -Werror             treat warnings as errors
 -XdbgST             launch StringTemplate visualizer on generated code
 -XdbgSTWait         wait for STViz to close before continuing
 -Xforce-atn         use the ATN simulator for all predictions
 -Xlog               dump lots of logging info to antlr-timestamp.log
 -Xexact-output-dir  all output goes into -o dir regardless of paths/package

5. pip3 install antlr4-python3-runtime
    1. outputs: Collecting antlr4-python3-runtime
  Downloading antlr4_python3_runtime-4.13.1-py3-none-any.whl (144 kB)
     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 144.5/144.5 kB 3.5 MB/s eta 0:00:00
Installing collected packages: antlr4-python3-runtime
Successfully installed antlr4-python3-runtime-4.13.1

6. Test Antlr4 and JVox using the test.py in JupyterVox/PyASTVox/test


## 9. List of current pip packages
Package                           Version
--------------------------------- ----------
antlr4-python3-runtime            4.13.1
antlr4-tools                      0.2.1
argon2-cffi                       23.1.0
argon2-cffi-bindings              21.2.0
asttokens                         2.4.1
attrs                             23.1.0
beautifulsoup4                    4.12.2
bleach                            6.1.0
blinker                           1.7.0
certifi                           2023.11.17
cffi                              1.16.0
charset-normalizer                3.3.2
click                             8.1.7
comm                              0.2.0
debugpy                           1.8.0
decorator                         5.1.1
defusedxml                        0.7.1
executing                         2.0.1
fastjsonschema                    2.19.0
Flask                             3.0.0
gTTS                              2.5.0
idna                              3.6
install-jdk                       1.1.0
ipykernel                         6.27.1
ipython                           8.19.0
ipython-genutils                  0.2.0
itsdangerous                      2.1.2
jedi                              0.19.1
Jinja2                            3.1.2
jsonschema                        4.20.0
jsonschema-specifications         2023.12.1
jupyter_client                    8.6.0
jupyter-contrib-core              0.4.2
jupyter-contrib-nbextensions      0.7.0
jupyter_core                      5.5.1
jupyter-highlight-selected-word   0.2.0
jupyter-nbextensions-configurator 0.6.3
jupyterlab_pygments               0.3.0
lxml                              4.9.4
MarkupSafe                        2.1.3
matplotlib-inline                 0.1.6
mistune                           3.0.2
nbclient                          0.9.0
nbconvert                         7.13.1
nbformat                          5.9.2
nest-asyncio                      1.5.8
notebook                          6.4.12
packaging                         23.2
pandocfilters                     1.5.0
parso                             0.8.3
pexpect                           4.9.0
pip                               23.0.1
platformdirs                      4.1.0
prometheus-client                 0.19.0
prompt-toolkit                    3.0.43
psutil                            5.9.7
ptyprocess                        0.7.0
pure-eval                         0.2.2
pycparser                         2.21
Pygments                          2.17.2
python-dateutil                   2.8.2
PyYAML                            6.0.1
pyzmq                             25.1.2
referencing                       0.32.0
requests                          2.31.0
rpds-py                           0.15.2
Send2Trash                        1.8.2
setuptools                        66.1.1
six                               1.16.0
soupsieve                         2.5
stack-data                        0.6.3
terminado                         0.18.0
tinycss2                          1.2.1
tornado                           6.4
traitlets                         5.9.0
urllib3                           2.1.0
wcwidth                           0.2.12
webencodings                      0.5.1
Werkzeug                          3.0.1
