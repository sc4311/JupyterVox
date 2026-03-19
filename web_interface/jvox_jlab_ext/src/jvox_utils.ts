/**
 * JVox utilities
 */

import { INotebookTracker } from '@jupyterlab/notebook';
import { CodeEditor } from '@jupyterlab/codeeditor';
import { JVoxInfoPanel } from './jvox_info_panel';  

/**
 *  play sound
 */
// Create a static audio object for playing sound. This is because
// creating an audio object right before playing causes an awkward
// scilence/delay before the screenreading sound.
const audio = new Audio();
let reading_rate = 1.5; // increasing speech speed.
let infoPanel: JVoxInfoPanel | null = null; // singleton info panel instance, to be initialized when the extension is activated.

/**
 * Update the reading rate used by jvox_speak.
 * Called when the user changes the setting in the JupyterLab Settings UI.
 */
export function jvox_setReadingRate(rate: number): void {
    reading_rate = rate;
    console.log(`JVox: reading rate set to ${rate}`);
}

export async function jvox_speak(audioUrl: string){
    // Extract BASE64 encoded audio bytes, and play the audio
    audio.src = audioUrl;
    audio.playbackRate = reading_rate;

    try {
        await audio.play();
        console.log("Audio playing successfully.");
    } catch (err) {
        console.error("Playback failed. Make sure you've interacted with the page.", err);
    }
}

/**
 * Common function to process JVox server audio response
 * @param response 
 */
/*
export async function jvox_handleAudioResponse(response: Response)
{
    console.debug("JVox audio response:", response);

    // Unpack JSON
    const data = await response.json();

    // Access the speech in text and audio
    const speechText = data.speech;
    const base64Audio = data.audio;

    console.debug("speech text:", speechText);

    // Extract BASE64 encoded audio bytes, and play the audio
    const audioUrl = `data:audio/mpeg;base64,${base64Audio}`;
    jvox_speak(audioUrl);
} */

// get the text at, and the position of, current cursor
export function jvox_getLineAndCursor(notebookTracker: INotebookTracker
): { lineText: string | undefined, 
    line: number, 
    column: number, 
    editor: CodeEditor.IEditor } | null {
    const panel = notebookTracker.currentWidget;
    if (!panel) {
        console.warn('JVox: No active notebook');
        return null;
    }

    const cell = panel.content.activeCell;
    if (!cell) {
        console.warn('JVox: No active cell');
        return null;
    }

    const editor = cell.editor;
    if (!editor) {
        console.warn('JVox: No active editor');
        return null;
    }

    const cursorPos = editor.getCursorPosition()
    const text = editor.getLine(cursorPos.line)

    return {
        lineText: text,
        line: cursorPos.line,
        column: cursorPos.column,
        editor: editor,
    };
}

// get the text being selected at current cursor, returns the selected
// text. If not selection return empty string; if error, return null.
export function jvox_getSelection(notebookTracker: INotebookTracker
): { text: String } | null {
    const panel = notebookTracker.currentWidget;
    if (!panel) {
        console.warn('JVox: No active notebook');
        return null;
    }

    const cell = panel.content.activeCell;
    if (!cell) {
        console.warn('JVox: No active cell');
        return null;
    }

    const editor = cell.editor;
    if (!editor) {
        console.warn('JVox: No active editor');
        return null;
    }

    const selection = editor.getSelection()

    // Get the start and end positions of the selection
    const { start, end } = selection;

    // If the selection is collapsed (no actual selection), return null
    if (start.line === end.line && start.column === end.column) {
        return null;
    }

    let selectedText = '';
    if (start.line === end.line) {
        // Selection is within a single line
        const lineText = editor.getLine(start.line);
        if (lineText !== undefined && lineText !== null) {
            selectedText = lineText.substring(start.column, end.column);
        }
    } else {
        // Selection spans multiple lines
        // Get text from the first line
        const firstLineText = editor.getLine(start.line);
        if (firstLineText !== undefined && firstLineText !== null) {
            selectedText += firstLineText.substring(start.column) + '\n';
        }

        // Get text from the middle lines
        for (let line = start.line + 1; line < end.line; line++) {
            const midLineText = editor.getLine(line);
            if (midLineText !== undefined && midLineText !== null) {
                selectedText += midLineText + '\n';
            }
        }

        // Get text from the last line
        const lastLineText = editor.getLine(end.line);
        if (lastLineText !== undefined && lastLineText !== null) {
            selectedText += lastLineText.substring(0, end.column);
        }
    }

    return { text: selectedText };
}

export function jvox_updateInfoPanel(message: string): void {
    if (infoPanel) {
        console.debug("Updating JVox info panel with message:", message);
        infoPanel.showMessage(message);
    } else {
        console.warn("JVox: Info panel is not initialized yet.");
    }
}

export function jvox_setInfoPanel(panel: JVoxInfoPanel): void {
    infoPanel = panel;
}
