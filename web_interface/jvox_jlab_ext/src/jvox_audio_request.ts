/**
 * JVox utilities
 */

import { jvox_speak, jvox_updateInfoPanel } from "./jvox_utils";

import { requestAPI } from "./request";


/**
 * 
 */
export function jvox_readSpeech(textToRead: String){
    // request audio mp3 from server
    // send line to server extension
    const dataToSend = { speech: textToRead };
    requestAPI('audio', {
        body: JSON.stringify(dataToSend),
        method: 'POST'
    })
        .then(response => {
            console.debug("JVox audio response:", response);

            jvox_handleAudioResponse(response);
        })
        .catch(reason => {
            console.error(
                `Error on JVox audio with ${dataToSend}.\n${reason}`
            );
        });
    
}

/**
 * Process JVox server audio response
 * @param response: server response from Audio endpoint
 */
async function jvox_handleAudioResponse(response: Response)
{
    console.debug("JVox audio response:", response);

    // Unpack JSON
    const data = await response.json();

    // Access the speech in text and audio
    const speechText = data.speech;
    const base64Audio = data.audio;

    console.debug("speech text:", speechText);
    jvox_updateInfoPanel(speechText); // update the info panel with the speech text

    // Extract BASE64 encoded audio bytes, and play the audio
    const audioUrl = `data:audio/mpeg;base64,${base64Audio}`;
    jvox_speak(audioUrl);
}