console.log("JVox injected script starts.")
console.log("Monaco handle from window.monaco:")
console.log(window.monaco)

// Iterate over the editors (i.e., cells) to find the one with active keyboard
// focus. Get the cursor position (line and col) of the cursor, than extract
// the text of the line where the cursor is at. 
// Returns the text of line.
function jvox_get_cursor_line(){
    // get all the cursors
    var editors = window.monaco.editor.getEditors()

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

           console.log("jvox_inject: line at cursor from monaco: ", line);
       }
    }
    
    return line;
}



// add event handler to response to content script's request of
// statement line at cursor
document.addEventListener('jvox_request_stmt', function (e) {
    // console.log(e)
    let data = e.detail;
    console.log('jvox_inject: cursor-stmt request received', data);

    // send the line at cursor back to the content script
    let stmt_line = jvox_get_cursor_line();
    document.dispatchEvent(new CustomEvent('jvox_stmt_reply',
					   {detail: stmt_line}));
});
