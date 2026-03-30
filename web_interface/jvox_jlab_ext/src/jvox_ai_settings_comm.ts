/**
 * JVox AI Settings Comm
 *
 * Opens a Comm channel to the kernel's jvox_ai_settings_comm IPython
 * extension so the frontend can push AI backend settings (ai_client,
 * api_key) into the kernel for use by the %%jvoxAI cell magic.
 *
 * The kernel-side extension is loaded automatically:
 *   %load_ext jvox_ai_magics.jvox_ai_settings_comm
 */

import { INotebookTracker } from '@jupyterlab/notebook';
import { IKernelConnection } from '@jupyterlab/services/lib/kernel/kernel';
import { JVoxSettings } from './jvox_settings';

export class JVoxAiSettingsComm {
    private _comm: any = null;
    private _extensionLoaded: boolean = false;
    private _settings: JVoxSettings;

    constructor(settings: JVoxSettings) {
        this._settings = settings;
    }

    /**
     * Load the IPython extension in the kernel and open the Comm channel.
     * Should be called when a kernel becomes available.
     */
    public async setup(tracker: INotebookTracker): Promise<void> {
        const kernel = tracker.currentWidget?.context?.sessionContext?.session?.kernel;
        if (!kernel) {
            console.debug('JVox AiSettingsComm: No kernel available yet.');
            return;
        }

        // Avoid re-setup if already connected to this kernel
        if (this._comm) {
            console.debug('JVox AiSettingsComm: Comm already open.');
            return;
        }

        await this._loadExtensionAndOpenComm(kernel);
    }

    /**
     * Send the current AI settings to the kernel.
     * Can be called any time after setup() succeeds.
     */
    public sendSettings(): void {
        if (!this._comm) {
            console.debug('JVox AiSettingsComm: Comm not open, cannot send settings.');
            return;
        }

        const data = {
            ai_client: this._settings.aiClient,
            api_key: this._settings.geminiApiKey,
        };

        try {
            this._comm.send(data);
            console.log('JVox AiSettingsComm: Sent settings to kernel:', {
                ai_client: data.ai_client,
                api_key: data.api_key ? '(set)' : '(empty)',
            });
        } catch (e) {
            console.error('JVox AiSettingsComm: Failed to send settings.', e);
        }
    }

    private async _loadExtensionAndOpenComm(kernel: IKernelConnection): Promise<void> {
        // Load the IPython extension in the kernel if not yet loaded
        if (!this._extensionLoaded) {
            try {
                const future = kernel.requestExecute({
                    code: '%load_ext jvox_ai_magics.jvox_ai_settings_comm',
                    silent: true,
                    store_history: false,
                });
                await future.done;
                this._extensionLoaded = true;
                console.log('JVox AiSettingsComm: IPython extension loaded.');
            } catch (e) {
                console.error('JVox AiSettingsComm: Failed to load IPython extension.', e);
                return;
            }
        }

        // Open the Comm channel and send initial settings
        try {
            this._comm = kernel.createComm('jvox_ai_settings');

            this._comm.onClose = () => {
                console.log('JVox AiSettingsComm: Comm closed.');
                this._comm = null;
            };

            // Open with the current settings as initial payload
            await this._comm.open({
                ai_client: this._settings.aiClient,
                api_key: this._settings.geminiApiKey,
            }).done;
            console.log('JVox AiSettingsComm: Comm channel opened with initial settings.');
        } catch (e) {
            console.error('JVox AiSettingsComm: Failed to open Comm.', e);
            this._comm = null;
        }
    }

    /**
     * Close the Comm channel and reset state.
     */
    public dispose(): void {
        if (this._comm) {
            try {
                this._comm.close();
            } catch (e) {
                // Ignore errors during close
            }
            this._comm = null;
        }
        this._extensionLoaded = false;
    }
}
