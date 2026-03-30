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
import { JVoxSettings } from './jvox_settings';

import { JVoxKernelErrorComm } from './jvox_kernel_error_comm';
import { JVoxAiSettingsComm } from './jvox_ai_settings_comm';

// import { jvox_ReadChunk } from './jvox_read_chunk';
import { jvox_AiExplain } from './jvox_ai_explanation';
import { JVoxInfoPanelManager } from './jvox_info_panel';
import { jvox_setInfoPanelManager } from './jvox_utils';

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

		// initialize settings manager
		const jvoxSettings = new JVoxSettings();
		if (settingRegistry) {
			jvoxSettings
				.load(settingRegistry, plugin.id)
				.then(() => {
					// Apply current reading_rate value
					jvox_setReadingRate(jvoxSettings.readingRate);

					// Listen for future changes
					jvoxSettings.changed.connect(() => {
						jvox_setReadingRate(jvoxSettings.readingRate);
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

		// Set up the kernel Comm channel for structured error data
		const kernelErrorComm = new JVoxKernelErrorComm();
		kernelErrorComm.onError((errorData) => {
			jvox_debug.jvox_onKernelError(errorData);
		});

		// Set up the kernel Comm channel for AI settings
		const aiSettingsComm = new JVoxAiSettingsComm(jvoxSettings);

		// Re-send AI settings to the kernel whenever they change
		jvoxSettings.changed.connect(() => {
			aiSettingsComm.sendSettings();
		});

		// Set up Comm when kernel becomes available
		notebookTracker.currentChanged.connect(() => {
			const session = notebookTracker.currentWidget?.context?.sessionContext;
			if (session) {
				// When kernel changes (start/restart), re-setup the comm
				session.kernelChanged.connect(() => {
					kernelErrorComm.dispose();
					kernelErrorComm.setup(notebookTracker);
					aiSettingsComm.dispose();
					aiSettingsComm.setup(notebookTracker);
				});
				// Also try to set up now if kernel is already running
				if (session.session?.kernel) {
					kernelErrorComm.setup(notebookTracker);
					aiSettingsComm.setup(notebookTracker);
				}
			}
		});

		// register an event handler to process the 
		// NotebookActions.executed.connect(jvox_on_execution_finished);
		// Use a wrapper to pass the extra parameters
		NotebookActions.executed.connect((sender, args) => {
			jvox_debug.jvox_onExecutionFinished(sender,
				args,
				notebookTracker,
				lspManager);
		});

		/*
		// register an event handler to monitor the connection signal
		// to LSP server
		lspManager.connected.connect((manager, connectionData) => {
			const { connection, virtualDocument } = connectionData;
			jvox_debug.jvox_onLSPConnected(notebookTracker, manager, connection, virtualDocument);
		});
		*/
		// add commands for JVox debug support
		jvox_debug.jvox_registerDebugSupportCommands(app, notebookTracker, palette);

		// register JVox Read Chunk functions
		// Disabling read chunk function, as it may conflict with existing screen reader
		// const jvoxChunkReader = new jvox_ReadChunk()

		// jvoxChunkReader.jvox_registerReadChunkCommands(app, notebookTracker, palette);

		// register JVox AI explanation functions
		const jvoxAIExplainer = new jvox_AiExplain(jvoxSettings)
		jvoxAIExplainer.jvox_registerAiExplainCommands(app, notebookTracker, palette);

		// register JVox bottom information panel manager
		const infoPanelManager = new JVoxInfoPanelManager(app);
		infoPanelManager.registerCommands(palette);
		jvox_setInfoPanelManager(infoPanelManager);

		// Open the panel after the workspace is fully restored.
		app.restored.then(() => {
			infoPanelManager.open();
		});

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
