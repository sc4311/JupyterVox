//start script
console.log("JVox for Colab (Chrome) start")

// inject script into colab's page, so that we can access window.monaco
// code grab from https://stackoverflow.com/a/9517879
var s = document.createElement('script');
s.src = chrome.runtime.getURL('jvox_inject.js');
// remove to look clean? https://stackoverflow.com/a/11571763
s.onload = function() { this.remove(); }; 
(document.head || document.documentElement).appendChild(s); //reappend?

// handle the response (JVox screen reading) from the packground page.
//
// Data decoding part is from https://stackoverflow.com/a/10072601
function jvox_handle_response_from_bg(message) {

    console.log("jvox_content: received mp3 speech", message);

    // decode received data
    let received_data = JSON.parse(message.jvox_reading);
    console.log("jvox_content: recevied mp3 data after JSON parse", received_data)
    // received_data is an object. Convert it back to Unit8Array, then from "buffer"
    // to convert it back to ArrayBuffer
    recevied_array = new Uint8Array(received_data).buffer;
    console.log("jvox_content: decoded mp3 arrayBuffer:", recevied_array)

    // reconstruct the blob from the arrayBuffer, then use createObjectURL to
    // construct the Audio object to play.  Note that createObjectURL is not
    // allowed in the background script in Chrome. Based on
    // https://stackoverflow.com/a/58832311 and
    // https://stackoverflow.com/a/60215835
    const blob = new Blob([recevied_array], { type: "audio/mpeg" });
    var url = window.URL.createObjectURL(blob); // create an internal url to play mp3
    const w = new Audio();
    w.src = url;
    w.play();

    return;
}

// in case the communication with background script went wrong
function jvox_handle_error_with_gb(error) {
    console.log(`Error: ${error}`);
}

// sned the statement to background script
function jvox_send_stmt_to_background(stmt_text) {
    const sending = chrome.runtime.sendMessage({
	stmt_text: stmt_text,
    });
    sending.then(jvox_handle_response_from_bg,
		jvox_handle_error_with_gb);
}


// send an event to the injected script to request the line at cursor
function request_stmt_from_inject_js(){
    let data = {
        dummy: "nothing", // dumpy data, for future extentions
	dummy2: "nothing2"
    };

    document.dispatchEvent(new CustomEvent('jvox_request_stmt', {detail: data}));
}

// handler for JVox hotkey, alt+n.
function jvox_keyboard_shortcut(e) {    
    if (e.altKey && e.code === 'KeyN') { // alt+n
        console.log("Jvox: alt+n pressed");
        //line = jvox_get_cursor_line(); // get the line at cursor
      	//jvox_gen_speech_sound("12+13") // call JVox to read the line
      	request_stmt_from_inject_js();
    }
}
// register the handler
document.addEventListener('keyup', jvox_keyboard_shortcut, false);

// add event handler to response to injected script's statement line
// reading
document.addEventListener('jvox_stmt_reply', function (e) {
    // console.log(e)
    let stmt = e.detail;
    console.log('jvox_content: cursor stmt received', stmt);
    // send the statement to background to obtain speech from JVox server
    jvox_send_stmt_to_background(stmt);
});

//var audio = new Audio('https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3');
//audio.play();
