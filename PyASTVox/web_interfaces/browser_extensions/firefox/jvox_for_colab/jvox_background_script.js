browser.runtime.onInstalled.addListener(() => {
    console.log("background script started")
});

// send the statement to JVox server to obtain the reading as mp3, than play the
// sound. Note, need to change the IP (maybe also url), if server configuration 
// changes.
function jvox_gen_speech_sound(stmt_text){
  console.log("sending line: " + stmt_text)
  
  // encode the data
  // 
  //var surl = "http://3.144.13.232/jvox/speech3/post";
  var surl = " http://localhost:5000/speech3/post";
  //var surl = "https://example.com"
  var xmlHttp = new XMLHttpRequest();
	xmlHttp.responseType = "blob"; // response is mp3 byte stream
	xmlHttp.open("POST", surl, true); //async
	xmlHttp.setRequestHeader('Content-Type', 'application/json');
	
	xmlHttp.onload = function(e){ // response processing function
	    console.log(xmlHttp.response);
		//resp = xmlHttp.response; // response should be a blob of mp3 bytes
		console.log(xmlHttp.responseType);
		var url = window.URL.createObjectURL(xmlHttp.response); // create an internal url to play mp3
    		const w = new Audio();
    		w.src = url;
    		w.play();
	}

	xmlHttp.onerror = function (e) {
  		console.error(xmlHttp.statusText);
  		console.error(xmlHttp.status);
  		console.error(xmlHttp.response);
  		console.error(e)
	};
    
    // send the statement to read in JSON
    xmlHttp.send(JSON.stringify({
    		"stmt":stmt_text
	}));

	return
  
}

function handleMessage(request, sender, sendResponse) {
  console.log(`A content script sent a message: ${request.stmt_text}`);
  //var audio = new Audio('https://interactive-examples.mdn.mozilla.net/media/cc0-audio/t-rex-roar.mp3');
  //audio.play();
  jvox_gen_speech_sound(request.stmt_text);
  sendResponse({ response: "Response from background script" });
}

browser.runtime.onMessage.addListener(handleMessage);
