import {
    JupyterFrontEnd,
  //  JupyterFrontEndPlugin
} from '@jupyterlab/application';
 
import { INotebookTracker } from '@jupyterlab/notebook';
import { ICommandPalette } from '@jupyterlab/apputils';

import { requestAPI } from './request';
 
 //import { EditorView } from '@codemirror/view';
 
// import { CodeEditor } from '@jupyterlab/codeeditor';

import { jvox_getLineAndCursor, jvox_getSelection, jvox_speak, jvox_updateInfoPanel } from './jvox_utils';
 
import { JVoxCommandRegistry } from './jvox_command_registry';
import { JVoxSettings } from './jvox_settings';

export class jvox_AiExplain {

    private _settings: JVoxSettings;

    constructor(settings: JVoxSettings) {
        this._settings = settings;
    }

    // Register "read next chunk", "read previous chunk", and "read current chunk" commands
    public jvox_registerAiExplainCommands(
        app: JupyterFrontEnd,
        notebookTracker: INotebookTracker,
        palette: ICommandPalette) {

        // rext next chunk
        const { commands } = app;
        const commandObj = JVoxCommandRegistry.getCommandById('jvox:ai-code-explanation');
        if (!commandObj) {
            console.error("JVox command registry: command 'jvox:ai-code-explanation' not found.");
            return;
        }

        commands.addCommand(commandObj.id, {
            label: commandObj.label,
            execute: () => this.jvox_AiCodeExplain(notebookTracker)
        });

        app.commands.addKeyBinding({
            command: commandObj.id,
            keys: commandObj.hotkeys,
            selector: commandObj.selector
        });

        palette.addItem({ command: commandObj.id, category: 'JVox Operations' });

        // read previous chunk
        const prevCommandObj = JVoxCommandRegistry.getCommandById('jvox:ai-code-nested-operation-explanation');
        if (!prevCommandObj) {
            console.error("JVox command registry: command 'jvox:ai-code-nested-operation-explanation' not found.");
            return;
        }

        commands.addCommand(prevCommandObj.id, {
            label: prevCommandObj.label,
            execute: () => this.jvox_AiNestedCodeExplain(notebookTracker)
        });

        app.commands.addKeyBinding({
            command: prevCommandObj.id,
            keys: prevCommandObj.hotkeys,
            selector: prevCommandObj.selector
        });

        palette.addItem({ command: prevCommandObj.id, category: 'JVox Operations' });
    }

    private jox_getSelectionOrLine(notebookTracker: INotebookTracker): string | undefined {
        const selectionResult = jvox_getSelection(notebookTracker);
        if (selectionResult && selectionResult.text && selectionResult.text !== "") {
            console.debug("JVox AI Explanation section text:", selectionResult.text);
            return selectionResult.text as string;
        } else {
            const lineInfo = jvox_getLineAndCursor(notebookTracker);
            console.debug("JVox AI Explanation lineInfo:", lineInfo);
            return lineInfo ? lineInfo.lineText : undefined;
        }
    }

    /**
     * Explain the code at the cursor (line or selection) using an AI backend.
     * @param notebookTracker The INotebookTracker instance for tracking the active notebook and cell.
    **/
    private jvox_AiCodeExplain(notebookTracker:INotebookTracker)
    {
        console.debug("In jvox_AiCodeExplain.");

        let text_to_explain = this.jox_getSelectionOrLine(notebookTracker);

        // send line to server extension
        const dataToSend = { 
            statement: text_to_explain,
            command: "codeExplain",
            ai_client: this._settings.aiClient,
            api_key: this._settings.geminiApiKey,
         };
        requestAPI('AIExplain', {
            body: JSON.stringify(dataToSend),
            method: 'POST'
        })
            .then(reply => {
                console.log(reply);
                this.jvox_handleAiExplainResponse(reply);
            })
            .catch(reason => {
                console.error(
                    `Error on JVox read chunk with ${dataToSend}.\n${reason}`
                );
            });

        return;

    }

    /**
     * Explain the nested operations of code at the cursor (line or selection) using an AI backend.
     * @param notebookTracker The INotebookTracker instance for tracking the active notebook and cell.
    **/
    private jvox_AiNestedCodeExplain(notebookTracker:INotebookTracker)
    {
        console.debug("In jvox_AiNestedCodeExplain.")

        let text_to_explain = this.jox_getSelectionOrLine(notebookTracker);

        // send line to server extension
        const dataToSend = { 
            statement: text_to_explain,
            command: "nestedCodeExplain",
            ai_client: this._settings.aiClient,
            api_key: this._settings.geminiApiKey,
         };
        requestAPI('AIExplain', {
            body: JSON.stringify(dataToSend),
            method: 'POST'
        })
            .then(reply => {
                console.log(reply);
                this.jvox_handleAiExplainResponse(reply);
            })
            .catch(reason => {
                console.error(
                    `Error on JVox read chunk with ${dataToSend}.\n${reason}`
                );
            });

        return;

    }

    private async jvox_handleAiExplainResponse(
        response: Response)
    {
        console.debug("JVox AI Expalin response:", response);

        // Unpack JSON
        const data = await response.json();
      
        // Access the speech in text and audio
        const speechText = data.speech;
        console.debug("JVox AI Explain returns speech:", speechText);
        const base64Audio = data.audio;

        // play audio
        console.debug("speech text:", speechText);
        jvox_updateInfoPanel(speechText); // update the info panel with the speech text
        // Extract BASE64 encoded audio bytes, and play the audio
        const audioUrl = `data:audio/mpeg;base64,${base64Audio}`;
        jvox_speak(audioUrl);

        return;
    }

}