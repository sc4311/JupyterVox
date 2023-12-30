// ==UserScript==
// @name         JVox for Colab
// @namespace    http://tampermonkey.net/
// @version      2023-12-28
// @description  JupyterVox Chrome Plugin through TamperMonkey
// @author       You
// @match        https://colab.research.google.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=google.com
// @grant        none
// ==/UserScript==

console.log("hello");

function jvox_OnDidCreateEditor(editor){
    console.log("jvox: create editor")
    console.log(editor)
}

function jvox_get_cursor_line(){
    var editors = window.monaco.editor.getEditors()

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

           console.log("Line on cursor:" + line);
       }
    }
    return line;
}

window.onload = function()
{
    console.log("after load")
    console.log(window.monaco)
    window.monaco.editor.onDidCreateEditor((editor) => {
                    //console.log("create Editor xxx")
                    jvox_OnDidCreateEditor(editor)
                    });
};

// define a handler
function doc_keyUp(e) {

    // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time
    if (e.altKey && e.code === 'KeyN') {
        // call your function to do the thing
        //console.log("got key");
        jvox_get_cursor_line();
    }
}
// register the handler
document.addEventListener('keyup', doc_keyUp, false);
