import {
  JupyterFrontEnd,
} from '@jupyterlab/application';

import { INotebookTracker} from '@jupyterlab/notebook';
import { CodeMirrorEditor } from '@jupyterlab/codemirror';
import { ICommandPalette } from '@jupyterlab/apputils';

import { requestAPI } from './request';

import { jvox_speak, jvox_updateInfoPanel } from './jvox_utils';

import { JVoxCommandRegistry } from './jvox_command_registry'; // make sure this import is present


// read current line at cursor and send the line to the server to
// retrieve reading
function jvox_read_line(notebookTracker: INotebookTracker)
{
    const panel = notebookTracker.currentWidget;
    if (!panel) {
	console.warn('No active notebook');
	return;
    }
		
    const cell = panel.content.activeCell;
    if (!cell) {
	console.warn('No active cell');
	return;
    }
    
    const editor = cell.editor;
    if (!(editor instanceof CodeMirrorEditor)) {
	console.warn('Editor is not CodeMirror');
	return;
    }
    
    const cm = editor.editor; // CodeMirror 6 EditorView
    const cursor = cm.state.selection.main.head;
    const line = cm.state.doc.lineAt(cursor);
    
    const lineText = line.text;
    const lineNumber = line.number;
    
    // log the line
    console.log(`Line ${lineNumber}: ${lineText}`);

    // send line to server extension
    const dataToSend = { stmt: lineText };
    requestAPI('readline', {
	body: JSON.stringify(dataToSend),
	method: 'POST'
    })
	.then(reply => {
	    console.log(reply);
	    jvox_handle_readline_response(reply);
	})
	.catch(reason => {
	    console.error(
		`Error on JVox read single line with ${dataToSend}.\n${reason}`
	    );
	});
}

// register the command for JVox single-line screen read
export function jvox_add_readline_command(
    app: JupyterFrontEnd,
    notebookTracker: INotebookTracker,
    palette: ICommandPalette)
{

    // add new command that read current line at cursor
    const { commands } = app;
    
    // Use the command registry to get the current line command definition
    const commandObj = JVoxCommandRegistry.getCommandById('jvox:read-line-at-Cursor'); // note registry uses 'read-line-at-Cursor'
    if (!commandObj) {
        console.error("JVox command registry: command 'jvox:read-line-at-Cursor' not found.");
        return;
    }
    const commandID = commandObj.id;

    commands.addCommand(commandID, {
        label: commandObj.label,
        execute: () => jvox_read_line(notebookTracker)
    });
    
    app.commands.addKeyBinding({
        command: commandID,
        keys: commandObj.hotkeys,
        selector: commandObj.selector
    });
    
    palette.addItem({ command: commandID, category: 'JVox Operations' });
}

// Process the speech in text and audio from the server extension
async function jvox_handle_readline_response(response: Response){
    console.debug("JVox readline response:", response);

    // Unpack JSON
    const data = await response.json();
  
    // Access the speech in text and audio
    const speechText = data.speech;
    const base64Audio = data.audio;

    console.debug("Read line speech text:", speechText);
    jvox_updateInfoPanel(speechText); // update the info panel with the speech text

    // Extract BASE64 encoded audio bytes, and play the audio
    const audioUrl = `data:audio/mpeg;base64,${base64Audio}`;
    jvox_speak(audioUrl);

    return;
}
