import {
    JupyterFrontEnd
} from '@jupyterlab/application';

import { ICommandPalette, MainAreaWidget } from '@jupyterlab/apputils';

import { ReactWidget } from '@jupyterlab/ui-components';

import React from 'react';

import { JVoxCommandRegistry } from './jvox_command_registry';

/**
 * A React component that renders the info panel content.
 */
function InfoPanelComponent(props: { message: string }): React.ReactElement {
    return React.createElement(
        'div',
        { className: 'jvox-info-panel-content' },
        props.message
    );
}

/**
 * Inner ReactWidget that renders the info panel content.
 */
class JVoxInfoPanelContent extends ReactWidget {
    private _message: string = 'No information.';

    constructor() {
        super();
        this.addClass('jvox-info-panel');
    }

    public showMessage(text: string): void {
        this._message = text;
        this.update();
    }

    public clearMessages(): void {
        this._message = '';
        this.update();
    }

    protected render(): React.ReactElement {
        return React.createElement(InfoPanelComponent, { message: this._message });
    }
}

/**
 * Manager class for the JVox info panel.
 * Creates and disposes MainAreaWidget instances to show/hide the panel,
 * while preserving the message state across toggles.
 */
export class JVoxInfoPanelManager {
    private _app: JupyterFrontEnd;
    private _panel: MainAreaWidget<JVoxInfoPanelContent> | null = null;
    private _lastMessage: string = 'No information.';

    constructor(app: JupyterFrontEnd) {
        this._app = app;
    }

    /**
     * Whether the panel is currently open.
     */
    get isOpen(): boolean {
        return this._panel !== null && !this._panel.isDisposed;
    }

    /**
     * Display a text message. If the panel is open, update it immediately.
     * The message is also stored so it persists across toggles.
     */
    public showMessage(text: string): void {
        this._lastMessage = text;
        if (this._panel && !this._panel.isDisposed) {
            this._panel.content.showMessage(text);
        }
    }

    /**
     * Clear the panel content.
     */
    public clearMessages(): void {
        this._lastMessage = '';
        if (this._panel && !this._panel.isDisposed) {
            this._panel.content.clearMessages();
        }
    }

    /**
     * Open the info panel in the main area (split-bottom).
     */
    public open(): void {
        if (this._panel && !this._panel.isDisposed) {
            this._app.shell.activateById(this._panel.id);
            return;
        }
        const content = new JVoxInfoPanelContent();
        content.showMessage(this._lastMessage);
        this._panel = new MainAreaWidget({ content });
        this._panel.id = 'jvox-info-panel';
        this._panel.title.label = 'JVox Info';
        this._panel.title.closable = true;
        this._app.shell.add(this._panel, 'main', { mode: 'split-bottom' });

        // Adjust the split ratio so the info panel is compact.
        this._adjustSplitRatio();
    }

    /**
     * Close and dispose the info panel.
     */
    public close(): void {
        if (this._panel && !this._panel.isDisposed) {
            this._panel.dispose();
        }
        this._panel = null;
    }

    /**
     * Toggle the panel open/closed.
     */
    public toggle(): void {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    /**
     * Register the toggle command and hotkey for the info panel.
     */
    public registerCommands(palette: ICommandPalette): void {
        const { commands } = this._app;
        const commandObj = JVoxCommandRegistry.getCommandById('jvox:toggle-info-panel');
        if (!commandObj) {
            console.error("JVox command registry: command 'jvox:toggle-info-panel' not found.");
            return;
        }

        commands.addCommand(commandObj.id, {
            label: commandObj.label,
            execute: () => {
                this.toggle();
            }
        });

        this._app.commands.addKeyBinding({
            command: commandObj.id,
            keys: commandObj.hotkeys,
            selector: commandObj.selector
        });

        palette.addItem({ command: commandObj.id, category: 'JVox Operations' });
    }

    /**
     * Adjust the DockPanel split ratio so the info panel takes less vertical space.
     */
    private _adjustSplitRatio(): void {
        requestAnimationFrame(() => {
            try {
                const dockPanel = (this._app.shell as any)._dockPanel;
                if (dockPanel && dockPanel.saveLayout) {
                    const layout = dockPanel.saveLayout();
                    if (layout.main &&
                        layout.main.type === 'split-area' &&
                        layout.main.orientation === 'vertical' &&
                        layout.main.sizes) {
                        const n = layout.main.sizes.length;
                        layout.main.sizes = layout.main.sizes.map(
                            (_: number, i: number) => (i === n - 1) ? 0.2 : 0.8 / (n - 1)
                        );
                        dockPanel.restoreLayout(layout);
                    }
                }
            } catch (e) {
                console.warn('JVox: Could not adjust info panel split size', e);
            }
        });
    }
}
