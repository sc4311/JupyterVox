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