/**
 * JVox Kernel Error Comm
 * 
 * Opens a Comm channel to the kernel's jvox_error_comm IPython extension
 * to receive structured error information (type, message, line, column)
 * after each cell execution.
 * 
 * The kernel-side extension must be loaded first:
 *   %load_ext jvox_jlab_ext.jvox_error_comm
 */

import { INotebookTracker } from '@jupyterlab/notebook';
import { IKernelConnection } from '@jupyterlab/services/lib/kernel/kernel';

/**
 * Structured error data received from the kernel via Comm
 */
export interface IJVoxKernelError {
	type: string;      // e.g., "SyntaxError", "TypeError"
	message: string;   // error message string
	line: number;      // 1-based line number, -1 if unavailable
	column: number;    // 1-based column number, -1 if unavailable
	end_line: number;  // 1-based end line, -1 if unavailable
	end_column: number; // 1-based end column, -1 if unavailable
	text: string;      // source text of the error line
}

/**
 * Callback type for when a kernel error is received
 */
export type JVoxKernelErrorCallback = (error: IJVoxKernelError) => void;

/**
 * Manages the Comm channel to the kernel for receiving structured error data.
 */
export class JVoxKernelErrorComm {
	private _comm: any = null;
	private _callback: JVoxKernelErrorCallback | null = null;
	private _extensionLoaded: boolean = false;

	/**
	 * Register a callback to be invoked when the kernel sends error data.
	 */
	public onError(callback: JVoxKernelErrorCallback): void {
		this._callback = callback;
	}

	/**
	 * Load the IPython extension in the kernel and open the Comm channel.
	 * Should be called when a kernel becomes available.
	 */
	public async setup(tracker: INotebookTracker): Promise<void> {
		const kernel = tracker.currentWidget?.context?.sessionContext?.session?.kernel;
		if (!kernel) {
			console.debug('JVox KernelErrorComm: No kernel available yet.');
			return;
		}

		// Avoid re-setup if already connected to this kernel
		if (this._comm) {
			console.debug('JVox KernelErrorComm: Comm already open.');
			return;
		}

		await this._loadExtensionAndOpenComm(kernel);
	}

	/**
	 * Load the IPython extension and open the Comm channel.
	 */
	private async _loadExtensionAndOpenComm(kernel: IKernelConnection): Promise<void> {
		// Load the IPython extension in the kernel if not yet loaded
		if (!this._extensionLoaded) {
			try {
				const future = kernel.requestExecute({
					code: '%load_ext jvox_jlab_ext.jvox_error_comm',
					silent: true,
					store_history: false
				});
				await future.done;
				this._extensionLoaded = true;
				console.log('JVox KernelErrorComm: IPython extension loaded.');
			} catch (e) {
				console.error('JVox KernelErrorComm: Failed to load IPython extension.', e);
				return;
			}
		}

		// Open the Comm channel
		try {
			this._comm = kernel.createComm('jvox_error_info');

			this._comm.onMsg = (msg: any) => {
				const data = msg.content.data as IJVoxKernelError;
				console.log('JVox KernelErrorComm: Received error data:', data);

				if (this._callback) {
					this._callback(data);
				}
			};

			this._comm.onClose = () => {
				console.log('JVox KernelErrorComm: Comm closed.');
				this._comm = null;
			};

			await this._comm.open().done;
			console.log('JVox KernelErrorComm: Comm channel opened.');
		} catch (e) {
			console.error('JVox KernelErrorComm: Failed to open Comm.', e);
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
