// ==UserScript==
// @name         JVox for Colab
// @namespace    http://wwang.github.io/
// @version      0.1
// @description  Chrome plugin for JupyterVox through TamperMonkey
// @author       Wei Wang
// @match        https://colab.research.google.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=google.com
// @grant        GM_xmlhttpRequest
// ==/UserScript==

console.log("JVox plugin start.");

//var server_url = "http://3.144.13.232/jvox";
var server_url = "http://localhost:5000/";

function jvox_OnDidCreateEditor(editor){
    console.log("jvox: create editor")
    console.log(editor)
}

function jvox_get_cursor_line(){
    var editors = unsafeWindow.monaco.editor.getEditors()

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

function find_focused_cell(){
    var editors = unsafeWindow.monaco.editor.getEditors()

    var i = 0;
    var len = editors.length
    for(i = 0; i < len ; i++){
       var e = editors[i];
       //console.log(e)
       if (e.hasTextFocus()){
           console.log("Found focused cell:" + e)
           return e;
       }
    }

    return null;

}

// cmd can be "next", "pre", "cur"
// if is_start is True, jump to the corresponding token's start, otherwise to the end
function jvox_token_navigate(cmd, is_start){
    var editors = unsafeWindow.monaco.editor.getEditors()

    console.log("Moving cursor with cmd: " + cmd);

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
           var col_nu = e.getPosition().column;

           var cell_txt = e.getValue();
           var cell_txtArr = cell_txt.split('\n');
           var stmt_text = cell_txtArr[line_nu-1];

           console.log("Current Cursor position, line: " + line_nu + ", col: " + col_nu);

           // contact server to find the corresponding token's position
           col_nu = col_nu - 1; // monaco col nubmer starts at 1 instead 0, so minus 1
           var surl = server_url + "/tokennavigate";
           GM_xmlhttpRequest({
               method: "POST",
               url: surl,
               headers: {
                   "Content-Type": "application/json"
               },
               responseType: "json",
               data: JSON.stringify({"stmt":stmt_text, "cmd":cmd, "pos":col_nu.toString()}),
               onload: function(response) {
                   console.log(response.responseType);
                   console.log(response.response);

                   //get the new position
                   var new_col = -1
                   if (is_start){
                       new_col = response.response.start
                   }
                   else{
                       new_col = response.response.stop
                   }

                   if (new_col == -1){
                       // server returns -1, no next/pre token to jump to
                       return
                   }

                   // move the cursor to the new position
                   console.log("new col position is " + new_col);

                   var cell = find_focused_cell()
                   var line_nu = cell.getPosition().lineNumber;
                   new_col = new_col + 1; //adjust new_col since monaco's col number starts from 1 instead of 0

                   cell.setPosition({lineNumber: line_nu, column: new_col});

               },
               onerror: function (response) {
                   console.error("Speech Request error:" + response.statusText);
               }
           });
       }
    }


    return;
}

function jvox_gen_speech_sound(stmt_text){
    console.log("Getting sound speech for line: " + stmt_text)

    //var surl = "http://3.144.13.232/jvox/speech3/post";
    var surl = server_url + "/speech3/post"; //"http://localhost:5000/speech3/post";

    // send request to server to obtain speech mp3 file/blob as response
    GM_xmlhttpRequest({
        method: "POST",
        url: surl,
        headers: {
            "Content-Type": "application/json"
        },
        responseType: "blob",
        data: JSON.stringify({"stmt":stmt_text}),
        onload: function(response) {
            console.log(response);
            //console.log(xmlHttp.responseType);
            var url = window.URL.createObjectURL(response.response); //where value is the blob
            const w = new Audio();
            w.src = url;
            w.play();
        },
        onerror: function (response) {
            console.error("Speech Request error:" + response.statusText);
        }
    });

    return;
}

window.onload = function()
{
    console.log("after load")
    console.log(unsafeWindow.monaco)
    unsafeWindow.monaco.editor.onDidCreateEditor((editor) => {
                    //console.log("create Editor xxx")
                    jvox_OnDidCreateEditor(editor)
                    });
};

// key up even handler
function doc_keyUp(e) {

    if (e.altKey && e.code === 'KeyJ') {
        // alt+j => generate jvox speech
        var line = jvox_get_cursor_line();
        jvox_gen_speech_sound(line);
    }
    else if (e.altKey && e.code === 'KeyN') {
        // alt+n => jump to next token
        //console.log("got alt+righ key");
        jvox_token_navigate("next", true);
    }
    else if (e.altKey && e.code === 'KeyP') {
        // alt+n => jump to previous token
        //console.log("got alt+righ key");
        jvox_token_navigate("pre", true);
    }
    else if (e.altKey && e.code === 'KeyS') {
        // alt+n => jump to the start of current token
        //console.log("got alt+righ key");
        jvox_token_navigate("cur", true);
    }
    else if (e.altKey && e.code === 'KeyR') {
        // alt+n => jump to the end of current token
        //console.log("got alt+righ key");
        jvox_token_navigate("cur", false);
    }
}

// register the handler
document.addEventListener('keyup', doc_keyUp, false);
