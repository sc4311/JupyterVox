define([
    'base/js/namespace',
    'base/js/events'
    ], function(Jupyter, events) {

      var insert_cell = function() {
        Jupyter.notebook.
        insert_cell_above('code').
        set_text(`# HELLO from Planet Jupyter!`);
        Jupyter.notebook.select_prev();
        //Jupyter.notebook.execute_cell_and_select_below();
      };

      function http_get_speech(stmt)
      {
      	// encode the data
      	var surl = "http://localhost:5000/speech/" + encodeURIComponent(stmt);
    	var xmlHttp = new XMLHttpRequest();
    	xmlHttp.open( "GET", surl, false ); // false for synchronous request
    	xmlHttp.send( null );
	var arr = JSON.parse(xmlHttp.responseText);
	var text = arr.text;
	return text;
    	//return xmlHttp.responseText;
      }

      function http_post_speech(stmt_text)
      {
      	// encode the data
      	var surl = "http://localhost:5000/speech2/post";
    	var xmlHttp = new XMLHttpRequest();
	xmlHttp.open("POST", surl, false);
	xmlHttp.setRequestHeader('Content-Type', 'application/json');
    	xmlHttp.send(JSON.stringify({
    		"stmt":stmt_text
	}));
	var arr = JSON.parse(xmlHttp.responseText);
	var text = arr.text;
	return text;
    	//return xmlHttp.responseText;
      }

      function http_post_speech_with_mp3(stmt_text)
      {
      	// encode the data
      	var surl = "http://localhost:5000/speech3/post";
    	var xmlHttp = new XMLHttpRequest();
	xmlHttp.responseType = "blob";
	xmlHttp.open("POST", surl, true); //async
	xmlHttp.setRequestHeader('Content-Type', 'application/json');
	
	xmlHttp.onload = function(e){
		resp = xmlHttp.response;
		console.log(resp);
		console.log(xmlHttp.responseType);
		var url = window.URL.createObjectURL(resp); //where value is the blob
    		const w = new Audio();
    		w.src = url;
    		w.play();
	}

	xmlHttp.onerror = function (e) {
  		console.error(xhr.statusText);
	};


    	xmlHttp.send(JSON.stringify({
    		"stmt":stmt_text
	}));
	//var arr = JSON.parse(xmlHttp.responseText);
	//var text = arr.text;
	//return text;
    	//return xmlHttp.responseText;
	return
      }

      var run_my_task = function() {
        //Jupyter.notebook.
        //insert_cell_above('code').
        //set_text(`# HELLO from Planet Jupyter!`);
        //Jupyter.notebook.select_prev();
        //Jupyter.notebook.execute_cell_and_select_below();
        var cell = Jupyter.notebook.get_selected_cell();
    	var cm = cell.code_mirror;
    	var selectedText = cm.getSelection();
	var cell_text = cell.get_text();
	//alert(cell_text);
	//alert(selectedText);
	var cursor = cm.getCursor();
	var line_text = cm.getLine(cursor.line);
	console.log(cursor.line);
	console.log(cursor.ch);
	console.log(cell_text);
	console.log(line_text);
	// var speech = http_get_speech(line_text);
	//var speech = http_post_speech(line_text);
	//console.log(speech)
	// play audio
	// var audio = new Audio('https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3');
  	//audio.play();
	http_post_speech_with_mp3(line_text);
      };

      // Add Toolbar button
      var planetJupyterButton = function () {
          console.log();
          Jupyter.toolbar.add_buttons_group([
              Jupyter.keyboard_manager.actions.register ({
                  'help': 'Add planet jupyter cell',
                  'icon' : 'fa-paper-plane',
                  //'handler': insert_cell
                  'handler': run_my_task
              }, 'addplanetjupyter-cell', 'Planet Jupyter')
          ])
      }

      // Add Toolbar button
      var jvox_setup = function () {
          console.log("jvox start");

	  // register the action for jupyter vox
	  var action = {
                  	icon : 'fa-paper-plane',
			help : 'JupyterVox Screen Reader',
			help_index : 'eb',
			id : 'JupyterrVox',
			handler : run_my_task
	 };
	  var name = "JupyterVox";
	  var prefix = "jvox";
	  var keybinding = 'alt-n';

	 var registered_action = Jupyter.keyboard_manager.actions.register(action, name, prefix);

	 var command_mode_shortcuts = {};
	 command_mode_shortcuts[keybinding] =  registered_action;

	 //register keyboard shortucts with keyboard_manager
	 Jupyter.notebook.keyboard_manager.edit_shortcuts.add_shortcuts(command_mode_shortcuts);
	 Jupyter.toolbar.add_buttons_group([registered_action]);

      }


    // Run on start
    function load_ipython_extension() {
        // Add a default cell if there are no cells
        if (Jupyter.notebook.get_cells().length===1){
            insert_cell();
        }
        //planetJupyterButton();
	jvox_setup()
    }
    return {
        load_ipython_extension: load_ipython_extension
    };
});
