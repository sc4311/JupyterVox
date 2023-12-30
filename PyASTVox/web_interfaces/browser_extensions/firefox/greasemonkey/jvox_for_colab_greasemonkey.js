// ==UserScript==
// @name        JVox for Colab
// @namespace   http://wwang.github.io
// @include     *
// @version     1
// ==/UserScript==
console.log("hello");

function jvox_OnDidCreateEditor(editor){
    console.log("jvox: create editor")
    console.log(editor)
}

function jvox_get_cursor_line(){
    var editors = unsafeWindow.monaco.editor.getEditors()

    //for (const e of editors) {
     //   console.log(e);

    //}

    var i = 0;
    var len = editors.length
    for(i = 0; i < len ; i++){
       var e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           //console.log("has focus")
           //console.log(e.getValue())
           //console.log(e.getPosition())

           var line_nu = e.getPosition().lineNumber;
           var cell_txt = e.getValue();
           var cell_txtArr = cell_txt.split('\n');
           var line = cell_txtArr[line_nu-1];

           console.log("Line on cursor: " + line);
       }
    }
    return line;
}


function jvox_gen_speech_sound(stmt_text){
  console.log("get line: " + stmt_text)
  //var audio = new Audio('https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3');
 	//audio.play();
  // encode the data
  var surl = " http://3.144.13.232/jvox/speech3/post";
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

window.onload = function()
{
    console.log("after load")
    console.log(window.monaco)
    /*unsafeWindow.monaco.editor.onDidCreateEditor((editor) => {
                    //console.log("create Editor xxx")
                    jvox_OnDidCreateEditor(editor)
                    });*/
};

// define a handler
function doc_keyUp(e) {

    // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time
    if (e.altKey && e.code === 'KeyN') {
        // call your function to do the thing
        //console.log("got key");
        line = jvox_get_cursor_line();
      	jvox_gen_speech_sound(line)
    }
}
// register the handler
document.addEventListener('keyup', doc_keyUp, false);
