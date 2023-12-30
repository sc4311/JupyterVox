//start script
console.log("JVox for Colab (firefox) start")

// has to use wrappedJSObject, since monaco is created by the web page
monaco_h = window.wrappedJSObject.monaco

// Note: does not work in firefox, permission deined for object 
function jvox_OnDidCreateEditor(editor){
    console.log("jvox: create editor")
    console.log(editor)
}

// Iterate over the editors (i.e., cells) to find the one with active keyboard
// focus. Get the cursor position (line and col) of the cursor, than extract
// the text of the line where the cursor is at. 
// Returns the text of line.
function jvox_get_cursor_line(){
    // get all the cursors
    // has to use unsafeWindow to access the objects created by the web 
    // page (i.e., colab)
    // var editors = unsafeWindow.monaco.editor.getEditors()
    var editors = monaco_h.editor.getEditors()

    var i = 0;
    var len = editors.length
    for(i = 0; i < len ; i++){
       var e = editors[i];
       
       if (e.hasTextFocus()){
           // cell has focus
           var line_nu = e.getPosition().lineNumber; // cursor line num
           var cell_txt = e.getValue(); // all text in cell
           var cell_txtArr = cell_txt.split('\n'); // convert to array of lines
           var line = cell_txtArr[line_nu-1]; // extract the cursor line

           console.log("Line on cursor: " + line);
       }
    }
    return line;
}


// does not work in Firefox, note necessary anymore
window.onload = function()
{
    console.log("JVox for Colab: after load")
    console.log(window.monaco)
    /*unsafeWindow.monaco.editor.onDidCreateEditor((editor) => {
                    //console.log("create Editor xxx")
                    jvox_OnDidCreateEditor(editor)
                    });*/
};

// handler for JVox hotkey, alt+n.
function jvox_keyboard_shortcut(e) {
    
    if (e.altKey && e.code === 'KeyN') { // alt+n
        //console.log("got key");
        line = jvox_get_cursor_line(); // get the line at cursor
      	//jvox_gen_speech_sound(line) // call JVox to read the line
      	notifyBackgroundPage(line);
    }
}
// register the handler
document.addEventListener('keyup', jvox_keyboard_shortcut, false);

function handleResponse(message) {
  console.log(`Message from the background script: ${message.response}`);
}

function handleError(error) {
  console.log(`Error: ${error}`);
}

function notifyBackgroundPage(stmt_text) {
  const sending = browser.runtime.sendMessage({
    stmt_text: stmt_text,
  });
  sending.then(handleResponse, handleError);
}


// some test code
// var audio = new Audio('https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3');
// audio.play();
