import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { ISettingRegistry } from '@jupyterlab/settingregistry';

import { INotebookTracker, NotebookActions } from '@jupyterlab/notebook';
import { ICommandPalette } from '@jupyterlab/apputils';
import { ILSPDocumentConnectionManager } from '@jupyterlab/lsp';

import { requestAPI } from './request';

/**
 * JVox packages
 */
import { jvox_add_readline_command } from './jvox_read_single_line'
import { jvox_setReadingRate } from './jvox_utils'
import {
    jvox_debugSupport
} from './jvox_debug_support'

// import { jvox_ReadChunk } from './jvox_read_chunk';
import { jvox_AiExplain } from './jvox_ai_explanation';

/**
 * Initialization data for the jvox-jlab-ext extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
    id: 'jvox-jlab-ext:plugin',
    description: 'A JupyterLab extension for JVox for screen reading',
    autoStart: true,
    requires: [INotebookTracker, ICommandPalette, ILSPDocumentConnectionManager],
    optional: [ISettingRegistry],
    activate: (
	app: JupyterFrontEnd,
	notebookTracker: INotebookTracker,
	palette: ICommandPalette,
	lspManager: ILSPDocumentConnectionManager,
	settingRegistry: ISettingRegistry | null
    ) => {
		console.log('JupyterLab extension jvox-jlab-ext is activated!');

		// initialize setting registry
		if (settingRegistry) {
			settingRegistry
				.load(plugin.id)
				.then(settings => {
					console.log('jvox-jlab-ext settings loaded:', settings.composite);

					// Apply current reading_rate value
					const rate = settings.get('reading_rate').composite as number;
					jvox_setReadingRate(rate);

					// Listen for future changes
					settings.changed.connect(() => {
						const updatedRate = settings.get('reading_rate').composite as number;
						jvox_setReadingRate(updatedRate);
					});
				})
				.catch(reason => {
					console.error('Failed to load settings for jvox-jlab-ext.', reason);
				});
		}

		// server extension connection test
		requestAPI('hello')
			.then(response => {
				jvox_server_hello_test(response);
			})
			.catch(reason => {
				console.error(
					`The jvox_jlab_ext server extension appears to be missing.\n${reason}`
				);
			});

		// add the command of JVox single-line screen read 
		jvox_add_readline_command(app, notebookTracker, palette);

		/*
		 * Register JVox debug support
		 */
		const jvox_debug = new jvox_debugSupport();
		// register an event handler to process the 
		// NotebookActions.executed.connect(jvox_on_execution_finished);
		// Use a wrapper to pass the extra parameters
		NotebookActions.executed.connect((sender, args) => {
			jvox_debug.jvox_onExecutionFinished(sender,
				args,
				notebookTracker,
				lspManager);
		});

		// register an event handler to monitor the connection signal
		// to LSP server
		lspManager.connected.connect((manager, connectionData) => {
			const { connection, virtualDocument } = connectionData;
			jvox_debug.jvox_onLSPConnected(notebookTracker, manager, connection, virtualDocument);
		});

		// add commands for JVox debug support
		jvox_debug.jvox_registerDebugSupportCommands(app, notebookTracker, palette);

		// register JVox Read Chunk functions
		// Disabling read chunk function, as it may conflict with existing screen reader
		// const jvoxChunkReader = new jvox_ReadChunk()

		// jvoxChunkReader.jvox_registerReadChunkCommands(app, notebookTracker, palette);

		// register JVox AI explanation functions
		const jvoxAIExplainer = new jvox_AiExplain()
		jvoxAIExplainer.jvox_registerAiExplainCommands(app, notebookTracker, palette);

	}
};

// A simple async function to print the reponse form "hello" endpoint,
// for testing server connection
async function jvox_server_hello_test(response: Response)
{
    const data = await response.json();
    console.log(data);

    return;
}

export default plugin;
