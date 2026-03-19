import {
    JupyterFrontEnd
} from '@jupyterlab/application';

import { ICommandPalette } from '@jupyterlab/apputils';

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
 * A bottom information panel for JVox, based on ReactWidget.
 * Displays general-purpose text messages pushed from the extension.
 */
export class JVoxInfoPanel extends ReactWidget {
    private _message: string = 'No information.';

    constructor() {
        super();
        this.id = 'jvox-info-panel';
        this.title.label = 'JVox Info';
        this.title.closable = true;
        this.addClass('jvox-info-panel');
    }

    /**
     * Display a text message in the panel.
     */
    public showMessage(text: string): void {
        this._message = text;
        this.update();
    }

    /**
     * Clear the panel content.
     */
    public clearMessages(): void {
        this._message = '';
        this.update();
    }

    /**
     * Render the React content of the panel.
     */
    protected render(): React.ReactElement {
        return React.createElement(InfoPanelComponent, { message: this._message });
    }

    /**
     * Register the toggle command for the info panel.
     */
    public registerCommands(
        app: JupyterFrontEnd,
        palette: ICommandPalette
    ): void {
        const { commands } = app;
        const commandObj = JVoxCommandRegistry.getCommandById('jvox:toggle-info-panel');
        if (!commandObj) {
            console.error("JVox command registry: command 'jvox:toggle-info-panel' not found.");
            return;
        }

        commands.addCommand(commandObj.id, {
            label: commandObj.label,
            execute: () => {
                if (this.isVisible) {
                    this.hide();
                } else {
                    this.show();
                }
            }
        });

        app.commands.addKeyBinding({
            command: commandObj.id,
            keys: commandObj.hotkeys,
            selector: commandObj.selector
        });

        palette.addItem({ command: commandObj.id, category: 'JVox Operations' });
    }
}
