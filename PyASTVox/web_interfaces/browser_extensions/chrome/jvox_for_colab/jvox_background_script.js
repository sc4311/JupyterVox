chrome.runtime.onInstalled.addListener(() => {
    console.log("JVox background script started")
});

// async function that converts the mp3 blob from JVox server to ArrayBuffer, so
// that we can late encode the ArrayBuffer into Unit8Array, to send back to the
// content script. "Async" allows "await" on this conversion so that we can stay
// somewhat synchronous in the caller.  Implemented as a Promise, from
// https://stackoverflow.com/a/55152476.
//
// Data encoding part is from https://stackoverflow.com/a/10072601.
async function async_blob_2_array(blob) {
    // wrapped the file read in a promise, and only resolve at the
    // onloadend event.
    let result = await new Promise((resolve) => {
        let fileReader = new FileReader();
        fileReader.onloadend = (e) => resolve(fileReader.result);
        fileReader.readAsArrayBuffer(blob);
    });

    console.log("jvox_gb: bloc read result", result);
    var arry = Array.from(new Uint8Array(result))

    return arry;
}

// async function to communicate with JVox server to obtain reading in mp3
// "Async” allows "await" in the caller.
// "fetch" part obtain from JS document：
// https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
async function jvox_gen_speech_sound(stmt_line) {
    // send statement to JVox server
    // need to change server ip accordingly
    let surl = "http://3.144.13.232/jvox/speech3/post";
    let data = {"stmt":stmt_line}
  
    const response = await fetch(surl, {
	method: "POST",
	mode: "cors",
	cache: "no-cache",
	credentials: "same-origin",
	headers: {
	    "Content-Type": "application/json",
	},
	redirect: "follow", 
	referrerPolicy: "no-referrer", 
	body: JSON.stringify(data), // body data type must match "Content-Type" header
    });

    console.log("jvox_bg: got reply type:",
		response.headers.get("content-type"))

    // conver the response blob to ArrayBuffer for communication with content script
    let blob = await response.blob() // wait the response blob to resolve
    console.log("jvox_bg: get reply blob", blob)
    let arry = await async_blob_2_array(blob)

    return arry; 
}

/*
 * Function to handle content script's message of sending a statement to read.
 * Cannot be an "async" function to allow correct sendResponse behavior, base on
 * https://stackoverflow.com/a/53024910.
 *
 * Since this function cann't be async, then we can't use "await" on
 * jvox_gen_speech_sound. So "then" as a call back is the only solution.
 *
 * JSON encoding part is from https://stackoverflow.com/a/10072601
 */
function jvox_bg_hand_send_statement(request, sender, sendResponse) {
    console.log(`jvox_bg: ${request.stmt_text}`);
  
    // generate speech from JVox server, and encode returned bolb/ArrayBuffer
    // into JSON
    jvox_gen_speech_sound(request.stmt_text).then(arry =>{
	console.log("jvox_bg: got Unit8Array", arry)
	// encode Unit8Array into json
	let data = {data: arry}
	let json = JSON.stringify(arry)
	console.log("jvox_bg: JSON encoded Unite8Array", json)
	// send back to content script
	sendResponse({ jvox_reading: json});
    });
    
    // must return true to keep the communication channe alive. Otherwise,
    // content script will receive undefined as response. Seems to be a Chrome
    // bug: see, https://stackoverflow.com/a/53024910 and
    // https://crbug.com/1185241
    return true;
}

// add listener to handle send statement message
chrome.runtime.onMessage.addListener(jvox_bg_hand_send_statement);
