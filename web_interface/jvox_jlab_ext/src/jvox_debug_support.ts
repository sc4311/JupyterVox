import {
   JupyterFrontEnd,
 //  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { INotebookTracker } from '@jupyterlab/notebook';
import { ICommandPalette } from '@jupyterlab/apputils';

import {
	ILSPDocumentConnectionManager,
	ILSPConnection,
	VirtualDocument,
	IVirtualPosition
} from '@jupyterlab/lsp';

import { CodeEditor } from '@jupyterlab/codeeditor';

// data types use for communication with LSP server
import * as lsProtocol from 'vscode-languageserver-protocol';

import { jvox_readSpeech } from './jvox_audio_request';

import { JVoxCommandRegistry } from './jvox_command_registry';

export class jvox_debugSupport {
	private documentUri: string = "";
	private diagnosticListenerRegistered: boolean = false;
	private diagnostics: jvox_diagnostic[] = [];

	private lastError: jvox_lastError | undefined = undefined;

	/**
	 * Define the handler function
	 * This captures the cell and the success status from the signal
	 */
	public jvox_onExecutionFinished(_: any,
		args: { cell: any; success: boolean },
		tracker: INotebookTracker,
		lspManager: ILSPDocumentConnectionManager) {
		console.log("cell executed.", tracker, lspManager);

		const { cell, success } = args;

		console.log(cell);

		// 1. Only act if the cell execution failed
		if (!success) {
			console.log("cell execution error!", cell.model);

			const metadata = cell.model.toJSON();
			const outputs = metadata.outputs as any[];

			console.log("Error output", outputs);

			// Find the error output
			const errorOutput = outputs.find(output => output.output_type === 'error');

			if (errorOutput) {
				const ename = errorOutput.ename;   // Error name (e.g., TypeError)
				const evalue = errorOutput.evalue; // Error message
				const traceback = errorOutput.traceback; // Stack trace array
				

				console.error(`Error Name: ${ename}`);
				console.error(`Error Message: ${evalue}`);
				console.error("Traceback:", traceback);

				const errorLineNo = this.jvox_getErrorLineNo(traceback);

				// only process SyntaxError, as LSP diagnostics only reports SyntaxError
				if (ename == "SyntaxError") {

					const diagnostic = this.jvox_findDiagnosticbyError(cell.editor, evalue, errorLineNo - 1);

					console.log("Matched Error to Diagnostic: ", diagnostic);

					// store this error as last error 
					if (diagnostic) {
						this.lastError = new jvox_lastError();
						this.lastError.diagnostic = diagnostic;
						this.lastError.message = evalue;
						this.lastError.type = ename;
						this.lastError.traceback = traceback;
						console.log("JVox last error object:", this.lastError);
					} else {
						this.lastError = undefined;
					}
				} else {
					// need to populate other fields for jvox_diagnotic, and process other error types
					this.lastError = new jvox_lastError();
					this.lastError.diagnostic = new jvox_diagnostic();
					this.lastError.diagnostic.cell = cell.editor;
					this.lastError.diagnostic.startCol = 0; // always set to 0 for now
					this.lastError.diagnostic.startLine = errorLineNo - 1;
					this.lastError.message = evalue;
					this.lastError.type = ename;
					this.lastError.traceback = traceback;
					console.log("JVox last error object:", this.lastError);
				}

				// read the last error out laud
				this.jvox_readLastError();
			}
		}
	}

	/**
	 * Remove the Python file name from the error message, and add error type to the begain.
	 * Some how the error message I got from the cell outputs has Python file name.
	 */
	private jvox_prepareErrorMessage(errorType: string, 
		errorMsg: string) : string {
		// Remove the text in the last parenthesis from error message
		const cleanedMessage = errorMsg.replace(/\s*\([^)]*\)\s*$/, '');

		const errorToRead = errorType + ": " + cleanedMessage;		

		return errorToRead;
	}
	/**
	 * Read last error out
	 * @returns 
	 */
	private jvox_readLastError() {

		if (!this.lastError) {
			console.debug("JVox: no last error to read");
			return;
		}
		
		const errorToRead = this.jvox_prepareErrorMessage(this.lastError.type, this.lastError.message);
		console.debug("JVox: Error message to read: ", errorToRead);

		jvox_readSpeech(errorToRead);

		return;
	}

	/**
	 * Get the line number of the error from the traceback
	 * @param traceback - The traceback array
	 * @returns The line number of the error, starting from 1
	 */
	private jvox_getErrorLineNo(traceback: string[]): number {
		// Most Python kernels return a traceback array
		// We join them and strip ANSI color codes for easier parsing
		const fullTraceback = traceback.join('\n');
		const cleanTraceback = fullTraceback.replace(/\u001b\[[0-9;]*m/g, '');

		// Find the line number in the cleaned traceback
		const lineMatch = cleanTraceback.match(/line (\d+)/);

		if (!lineMatch) return -1;

		console.log("Error line number: ", lineMatch[1]);

		return parseInt(lineMatch[1], 10);
	}

	/** 
	 * When LSP is connected, register an event handler to listen for diagnostics
	 */
	public jvox_onLSPConnected(tracker: INotebookTracker,
		lspManager: ILSPDocumentConnectionManager,
		connection: ILSPConnection,
		document: VirtualDocument) {
		// do nothing if already registered listener
		if (this.diagnosticListenerRegistered)
			return;

		// Get the path to the opened notebook of file
		const context = tracker.currentWidget?.context;
		if (!context) return;
		const path = context.path;

		console.log("path:", path);
		console.log("virtual document: ", document.uri);

		// if the document path is different from the virtual document uri, 
		// report error and return
		// compare the path and the virtual document uri
		if (path !== document.uri) {
			console.error("document path and virtual document uri are different.");
			return;
		}

		// Store this path
		if (this.documentUri === "") {
			this.documentUri = path;
		}

		/* // Get the widget adapter of opened document
		// adapaters are deprecated in JupyterLab 4.0.0, use connection instead
		const adapter = lspManager.adapters.get(path);
		if (!adapter) {
			return
		}
		console.log("adapter: ", adapter);

		// Get the associated virtual document of the opened document
		const virtualDocument = adapter.virtualDocument;
		if (!virtualDocument) {
			console.log("no virtual document.");
			return;
		}
		
		// Get the LSP connection of the virtual document.
		//const connection = lspManager.connections.get(virtualDocument.uri);
		if (!connection) {
			console.log("no connection for current document.");
			return;
		} */

		console.log("Connect: ", connection);

		console.log("Can do: ", connection.serverCapabilities);

		connection.serverNotifications['textDocument/publishDiagnostics'].connect(
			async (connection: ILSPConnection, diagnostics) => {
				console.log("Diagnotics: ", diagnostics);

				await this.jvox_handleDiagnostics(diagnostics, document);
			}
		);

		this.diagnosticListenerRegistered = true;

		// JupyterLab LSP does not support pull diagnostic, otherwise this should work
		// // try to pull diagnostics
		// // from https://jupyterlab.readthedocs.io/en/4.4.x/extension/extension_points.html#lsp-features
		// // and https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_diagnostic
		// const res = connection.clientRequests['textDocument/diagnostic'].request({
		//     textDocument: { uri: virtualDocument!.uri }
		// });

		// res.then(value => {
		//     console.log(value);
		// }).catch(e => console.error);


		return;
	}


	public async jvox_handleDiagnostics(
		response: lsProtocol.PublishDiagnosticsParams,
		document: VirtualDocument,
	) {
		// use optional chaining operator because the diagnostics message may come late (after the document was disposed)
		// if (!urisEqual(response.uri, document?.documentInfo?.uri)) {
		//   return;
		// }

		if (document.lastVirtualLine === 0) {
			return;
		}

		// clear the old array, this is not elegant...
		// should just update and completely redo the array.
		this.diagnostics = [];

		// iterative over diagnostics and store them
		response.diagnostics.forEach(diagnostic => {
			this.jvox_storeDiagnostics(document, diagnostic);
		});

	}

	private jvox_storeDiagnostics(document: VirtualDocument,
		diagnostic: lsProtocol.Diagnostic) {
		console.log("Storing diagnostic:", diagnostic);

		const d = diagnostic;

		const jvox_d = new jvox_diagnostic();

		// get the cell of the error
		const start = {
			line: d.range.start.line,
			ch: d.range.start.character
		} as IVirtualPosition;
		const editorAccessor = document.getEditorAtVirtualLine(start);
		jvox_d.cell = editorAccessor.getEditor()

		// convert diagnostic's document position to cell position

		const startInEditor = document.transformVirtualToEditor(start);
		if (startInEditor) {
			jvox_d.startLine = startInEditor.line;
			jvox_d.startCol = startInEditor.ch;
		}

		const end = {
			line: d.range.end.line,
			ch: d.range.end.character
		} as IVirtualPosition;
		const endInEditor = document.transformVirtualToEditor(end);
		if (endInEditor) {
			jvox_d.endLine = endInEditor.line;
			jvox_d.endCol = endInEditor.ch;
		}

		// copy other fields
		jvox_d.message = d.message;
		jvox_d.severity = d.severity;
		jvox_d.source = d.source;

		// add to list
		this.diagnostics.push(jvox_d);

		console.log("Stored jvox diagnostic:", jvox_d);

		return;
	}

	private jvox_findDiagnosticbyError(cell: CodeEditor.IEditor,
		errorMessage: string,
		line: number,
	): jvox_diagnostic | undefined {

		console.log("Finding diagnostic by error: ", errorMessage, " at line: ", line);

		for (const diagnostic of this.diagnostics) {
			// using only pyflakes source for now
			if (diagnostic.source !== "pyflakes")
				continue;

			// log both uuid and uuid of the cell
			console.log("Diagnostic uuid: ", diagnostic.cell?.uuid);
			console.log("Cell uuid: ", cell.uuid);
			if (diagnostic.cell?.uuid !== cell.uuid)
				continue;

			// log both start line and line
			console.log("Diagnostic start line: ", diagnostic.startLine);
			console.log("Line: ", line);
			if (diagnostic.startLine !== line)
				continue;

			// remove text in parenthesis from the error message
			const cleanErrorMessage = errorMessage.replace(/\(.*\)/, '');
			if (diagnostic.message.includes(cleanErrorMessage))
				return diagnostic;
		}
		return undefined;
	}

	
	/**
	 * Sets the cursor to the last error's line and column in the corresponding cell, if available.
	 * Assumes that this.lastError and its diagnostic are set.
	 * @param notebookTracker The tracker used to find the current notebook and cell.
	 * @param gotoColumn: whether to jump to column or just the beginning of the line.
	 */
	public jvox_gotoLastError(notebookTracker: INotebookTracker,
		gotoColumn: Boolean = false
	): void {
		console.log("JVox: going to last error column.")
		console.log("JVox: last error: ", this.lastError);
		console.log("JVox: last error diagnostic: ", this.lastError?.diagnostic);

		if (!this.lastError || !this.lastError.diagnostic || !this.lastError.diagnostic.cell) {
			console.debug("JVox: No last error or diagnostic/cell information to set cursor.");
			return;
		}

		const errorDiag: jvox_diagnostic = this.lastError.diagnostic;
		const editor: CodeEditor.IEditor = this.lastError.diagnostic.cell;

		let startLine = errorDiag.startLine;
		let startCol = errorDiag.startCol;

		if (!gotoColumn)
			startCol = 0;
		// Ensure startLine and startCol are valid (CodeMirror is 0-based)
		const position = { line: startLine, column: startCol };

		console.debug(`JVox setting cursor to ${editor} line ${startLine} column ${startCol}`);

		// set focus to cell
		editor.focus()
		// set cursor position
		editor.setCursorPosition(position);

		return;
		
		// the following code is generated by Cursor, kinda too complex
		// It works correctly, so I keep it here for reference
		/* const errorDiag = this.lastError.diagnostic;
		const cellModelUuid = this.lastError.diagnostic.cell.uuid;

		const panel = notebookTracker.currentWidget;
		if (!panel) {
			console.warn('JVox: No active notebook panel to set cursor.');
			return;
		}

		// Find the cell in the notebook with the matching uuid
		const cell = panel.content.widgets.find(cellWidget => {
			if(cellWidget.editor)
				return cellWidget.editor.uuid === cellModelUuid;
			else
				return null;
		});
		if (!cell) {
			console.warn('JVox: Could not find cell with the diagnostic uuid');
			return;
		}

		// Set this cell as the active cell
		panel.content.activeCellIndex = panel.content.widgets.indexOf(cell);

		const editor = cell.editor;
		if(!editor){
			console.warn("JVox: Cannot find the cell editor to jump to")
			return;
		}


		const { startLine, startCol } = errorDiag;
		// Ensure startLine and startCol are valid (CodeMirror is 0-based)
		const position = { line: startLine, column: startCol };
		if (editor.hasOwnProperty('setCursorPosition')) {
			editor.setCursorPosition(position);
		} else if ((editor as any).setSelection) {
			// Fallback for more generic editors
			(editor as any).setSelection({
				start: position,
				end: position
			});
		} else {
			console.warn('JVox: Unable to set cursor position in editor.');
		} */
	}

	// syntax check of current line
	/**
	 * Checks if there is a diagnostic that matches the current cursor position
	 * in the currently focused cell as determined by the notebook tracker.
	 * If found, reads the error message using jvox_readSpeech.
	 * If not found, reads "This line is correct".
	 * @param notebookTracker The tracker used to find the current active/focused cell.
	 */
	public jvox_readDiagnosticAtCursor(notebookTracker: INotebookTracker): void {
		const panel = notebookTracker.currentWidget;
		if (!panel || !panel.content || !panel.content.activeCell) {
			console.debug("JVox: cannot locate focused cell");
			return;
		}

		const cellWidget = panel.content.activeCell;
		const cellEditor = cellWidget.editor;
		if (!cellEditor) {
			console.debug("JVox: cannot obtain the editor of focused cell");
			return;
		}

		const cursor = cellEditor.getCursorPosition();
		const line = cursor.line;

		for (const diagnostic of this.diagnostics) {
			if (diagnostic.cell?.uuid !== cellEditor.uuid) {
				continue;
			}
			if (diagnostic.startLine === line) {
				/* const errorToRead = this.jvox_prepareErrorMessage(diagnostic.type, 
					diagnostic.message); */
				// Remove "(detected at line xxx)" from the message if present
				const cleanMessage = diagnostic.message.replace(/\s*\(detected at line \d+\)\s*$/, '');
				jvox_readSpeech(cleanMessage);
				return;
			}
		}
		jvox_readSpeech("This line is correct");
	}

	// Function to update diagnostic message with cell line number
	private jvox_getMessageWithCellLine(diagnostic: any): string {
		let updatedMessage = diagnostic.message;
		if (diagnostic.cell && typeof diagnostic.startLine === "number" && diagnostic.startLine >= 0) {
			const cellLineNum = diagnostic.startLine + 1;
			updatedMessage = updatedMessage.replace(
				new RegExp(`line\\s+\\d+\\b`, "g"),
				`line ${cellLineNum}`
			);
		}
		return updatedMessage;
	}

	/**
	 * Reads the error message of the first diagnostic of the currently focused cell.
	 * If there is no diagnostic, reads "This cell is correct".
	 * @param notebookTracker The tracker used to find the current active/focused cell.
	 */
	public jvox_readFirstDiagnosticOfCell(notebookTracker: INotebookTracker): void {
		const panel = notebookTracker.currentWidget;
		if (!panel || !panel.content || !panel.content.activeCell) {
			console.debug("JVox: cannot locate focused cell");
			return;
		}

		const cellWidget = panel.content.activeCell;
		const cellEditor = cellWidget.editor;
		if (!cellEditor) {
			console.debug("JVox: cannot obtain the editor of focused cell");
			return;
		}

		const firstDiagnostic = this.diagnostics.find(
			diagnostic => diagnostic.cell?.uuid === cellEditor.uuid
		);

		if (firstDiagnostic) {
			jvox_readSpeech(this.jvox_getMessageWithCellLine(firstDiagnostic));
			//jvox_readSpeech(firstDiagnostic.message);
		} else {
			jvox_readSpeech("This cell is correct");
		}
	}

	// register read last error command
	private jvox_registerReadLastErrorCommand(
		app: JupyterFrontEnd,
		notebookTracker: INotebookTracker,
		palette: ICommandPalette) {

		// add new command that reads last error
		const { commands } = app;
		const commandObj = JVoxCommandRegistry.getCommandById('jvox:read-last-error');
		if (!commandObj) {
			console.error("JVox command registry: command 'jvox:read-last-error' not found.");
			return;
		}

		commands.addCommand(commandObj.id, {
			label: commandObj.label,
			execute: () => this.jvox_readLastError()
		});

		app.commands.addKeyBinding({
			command: commandObj.id,
			keys: commandObj.hotkeys,
			selector: commandObj.selector
		});

		palette.addItem({ command: commandObj.id, category: 'JVox Operations' });
	}

	// register goto last error commands using JvoxCommandRegistry
	private jvox_registerGotoLastErrorCommand(
		app: JupyterFrontEnd,
		notebookTracker: INotebookTracker,
		palette: ICommandPalette) {

		const { commands } = app;

		const commandObj_gotoColumn = JVoxCommandRegistry.getCommandById('jvox:jump-to-last-error-column');
		const commandObj_gotoLineOnly = JVoxCommandRegistry.getCommandById('jvox:goto-last-error-line');

		if (!commandObj_gotoColumn) {
			console.error("JVox command registry: command 'jvox:jump-to-last-error-column' not found.");
			return;
		}
		if (!commandObj_gotoLineOnly) {
			console.error("JVox command registry: command 'jvox:goto-last-error-line' not found.");
			return;
		}

		// Register command for jumping to last error's line and column
		commands.addCommand(commandObj_gotoColumn.id, {
			label: commandObj_gotoColumn.label,
			execute: () => this.jvox_gotoLastError(notebookTracker, true)
		});

		app.commands.addKeyBinding({
			command: commandObj_gotoColumn.id,
			keys: commandObj_gotoColumn.hotkeys,
			selector: commandObj_gotoColumn.selector
		});

		// Register command for jumping to last error's line only
		commands.addCommand(commandObj_gotoLineOnly.id, {
			label: commandObj_gotoLineOnly.label,
			execute: () => this.jvox_gotoLastError(notebookTracker, false)
		});

		app.commands.addKeyBinding({
			command: commandObj_gotoLineOnly.id,
			keys: commandObj_gotoLineOnly.hotkeys,
			selector: commandObj_gotoLineOnly.selector
		});

		palette.addItem({ command: commandObj_gotoColumn.id, category: 'JVox Operations' });
		palette.addItem({ command: commandObj_gotoLineOnly.id, category: 'JVox Operations' });
	}

	// register verify current line command
	private jvox_registerVerifyLineCommand(
		app: JupyterFrontEnd,
		notebookTracker: INotebookTracker,
		palette: ICommandPalette) {

		const { commands } = app;
		const commandObj = JVoxCommandRegistry.getCommandById('jvox:verify-current-line');
		if (!commandObj) {
			console.error("JVox command registry: command 'jvox:verify-current-line' not found.");
			return;
		}
		const commandID = commandObj.id;

		commands.addCommand(commandID, {
			label: commandObj.label,
			execute: () => this.jvox_readDiagnosticAtCursor(notebookTracker)
		});

		app.commands.addKeyBinding({
			command: commandID,
			keys: commandObj.hotkeys,
			selector: commandObj.selector
		});

		palette.addItem({ command: commandID, category: 'JVox Operations' });
	}
	

	// register read first diagnostic of cell command
	private jvox_registerCheckCellSyntaxCommand(
		app: JupyterFrontEnd,
		notebookTracker: INotebookTracker,
		palette: ICommandPalette) {
		
		const { commands } = app;
		const commandObj = JVoxCommandRegistry.getCommandById('jvox:check-cell-syntax');
		if (!commandObj) {
			console.error("JVox command registry: command 'jvox:check-cell-syntax' not found.");
			return;
		}
		const commandID = commandObj.id;

		commands.addCommand(commandID, {
			label: commandObj.label,
			execute: () => this.jvox_readFirstDiagnosticOfCell(notebookTracker)
		});

		app.commands.addKeyBinding({
			command: commandID,
			keys: commandObj.hotkeys,
			selector: commandObj.selector
		});

		palette.addItem({ command: commandID, category: 'JVox Operations' });
	}

	// register the commands for JVox debug support
	public jvox_registerDebugSupportCommands(
		app: JupyterFrontEnd,
		notebookTracker: INotebookTracker,
		palette: ICommandPalette) {

		this.jvox_registerReadLastErrorCommand(app, notebookTracker, palette);
		this.jvox_registerGotoLastErrorCommand(app, notebookTracker, palette);
		this.jvox_registerVerifyLineCommand(app, notebookTracker, palette);
		this.jvox_registerCheckCellSyntaxCommand(app, notebookTracker, palette);
	}


	// public Diagnostics(
	// 	diagnostics: lsProtocol.Diagnostic[],
	// 	document: VirtualDocument,
	// )
	// {
	// 	diagnostics.forEach(diagnostic => {

	// 	    // has fields severity, source, message, range
	// 	    // see https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#diagnostic
	// 	    const d = diagnostic;
	// 	    console.log(d.severity, d.source, d.message, d.range);



	// 	    console.log("Virtual pos of start: ", start);

	// 	    const editorAccessor = document.getEditorAtVirtualLine(start);
	// 	    const editor = editorAccessor.getEditor()

	//         const startInEditor = document.transformVirtualToEditor(start);

	// 	    console.log("Editor: ", editor);
	// 	    if(editor){
	// 		console.log("Editor text: ", editor.getLine(0));
	// 	    }
	// 	    console.log("Start in editor: ", startInEditor);
	// 	});
	// }
}


/**
 * Storage class for LSP diagnostics
 */
class jvox_diagnostic {
	public severity: number | undefined = -1;
	public message: string = "";
	public source: string | undefined = "";
	public cell: CodeEditor.IEditor | null = null;
	public type: string = "";

	public startLine: number = -1; //from 0
	public startCol: number = -1; //from 0
	public endLine: number = -1; //from 0
	public endCol: number = -1; //from 0
}

/*
* Storage class for last error
*/
class jvox_lastError {
	public diagnostic: jvox_diagnostic | undefined = undefined;

	public message: string = "";
	public type: string = "";
	public traceback: string[] = [];

}




