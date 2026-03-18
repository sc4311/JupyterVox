import { Widget } from '@lumino/widgets';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { INotebookTracker } from '@jupyterlab/notebook';
import { ICommandPalette } from '@jupyterlab/apputils';
import { Cell, CodeCell } from '@jupyterlab/cells';
import { JVoxCommandRegistry } from './jvox_command_registry';

/**
 * A widget that displays supplementary information alongside a code cell's
 * editor.  The widget is inserted as a sibling of the CodeMirror editor
 * inside `.jp-InputArea`, creating a side-by-side layout.
 *
 * The DOM is built with ARIA attributes so that screen readers can discover
 * and navigate the panel independently of the code editor.
 */
export class JvoxInfoPanelWidget extends Widget {
    private _cellId: String;
    private _contentNode: HTMLElement;
    private _statusNode: HTMLElement;
    private parentCell: Cell | null = null;

    constructor(cellId: String) {
        super();
        this._cellId = cellId;

        // Root element
        this.addClass('jvox-info-plane');
        this.node.setAttribute('role', 'region');
        this.node.setAttribute(
            'aria-label',
            `Code information panel for cell ${cellId}`
        );
        this.node.setAttribute('tabindex', '0');

        // Status node for aria-live announcements
        this._statusNode = document.createElement('span');
        this._statusNode.className = 'jvox-info-plane-status';
        this._statusNode.setAttribute('role', 'status');
        this._statusNode.setAttribute('aria-live', 'polite');
        this._statusNode.style.position = 'absolute';
        this._statusNode.style.width = '1px';
        this._statusNode.style.height = '1px';
        this._statusNode.style.overflow = 'hidden';
        this._statusNode.style.clip = 'rect(0 0 0 0)';
        this.node.appendChild(this._statusNode);

        // Main content container
        this._contentNode = document.createElement('div');
        this._contentNode.className = 'jvox-info-plane-content';
        this.node.appendChild(this._contentNode);

        // Initial placeholder content
        this.setContent(
            '<p class="jvox-info-plane-placeholder">No information yet.</p>'
        );
    }

    /** Update the cell id (e.g., after cells are reordered). */
    updateCellId(cellId: String): void {
        this._cellId = cellId;
        this.node.setAttribute(
            'aria-label',
            `Code information panel for cell ${cellId}`
        );
    }

    /** Get the current cell id. */
    get cellId(): String {
        return this._cellId;
    }

    /**
     * Replace the content of the info plane with the given HTML string.
     * The content should use semantic HTML (lists, sections, paragraphs).
     */
    setContent(html: string): void {
        this._contentNode.innerHTML = html;
    }

    /**
     * Append an HTML fragment to the existing content.
     */
    appendContent(html: string): void {
        const fragment = document.createRange().createContextualFragment(html);
        this._contentNode.appendChild(fragment);
    }

    /** Clear all content and reset to placeholder. */
    clearContent(): void {
        this.setContent(
            '<p class="jvox-info-plane-placeholder">No information yet.</p>'
        );
    }

    /**
     * Announce a message to screen readers via the aria-live region,
     * without changing the visible content.
     */
    announce(message: string): void {
        this._statusNode.textContent = '';
        // Force re-announcement by clearing then setting after a microtask
        requestAnimationFrame(() => {
            this._statusNode.textContent = message;
        });
    }

    /**
     * Attach the info panel to a cell's input area, placing it below the code editor.
     * This is called by the manager when creating a new panel.  The panel is
     * inserted as a sibling of the CodeMirror editor, so it appears in the
     * input area but below the code editor.    
     */
    attachToCell(cell: Cell): void {
        const inputWrapper = cell.node.querySelector('.jp-Cell-inputWrapper');
        if (inputWrapper && inputWrapper.parentNode) {
            inputWrapper.parentNode.insertBefore(
                this.node,
                inputWrapper.nextSibling
            );
            this.parentCell = cell;
        }
    }

    /** Detach the info panel from its cell and remove it from the DOM. */
    detachFromCell(): void {
        if (this.parentCell) {
            const inputWrapper = this.parentCell.node.querySelector('.jp-Cell-inputWrapper');
            if (inputWrapper && inputWrapper.parentNode) {
                inputWrapper.parentNode.removeChild(this.node);
            }
            this.parentCell = null;
        }
    }
}

/**
 * Manages the lifecycle of JvoxInfoPanelWidget instances: one per code cell.
 *
 * Responsibilities:
 *  - Create an info panel for a code cell on demand.
 *  - Remove orphaned panels when cells are deleted.
 *  - Provide lookup by cell widget for other modules to push content.
 */
export class JvoxInfoPanelManager {
    private _tracker: INotebookTracker;
    // Keyed by the Cell widget's unique id
    private _panels: Map<string, JvoxInfoPanelWidget> = new Map();
    private _enabled: boolean = true;

    constructor(tracker: INotebookTracker, enabled: boolean = true) {
        this._tracker = tracker;
        this._enabled = enabled;

        // Listen for cell-list changes so we can remove orphaned panels
        this._tracker.widgetAdded.connect((_sender, panel) => {
            this._hookNotebookForCleanup(panel.content);
        });

        if (this._tracker.currentWidget) {
            this._hookNotebookForCleanup(this._tracker.currentWidget.content);
        }
    }

    /** Dynamically enable or disable the info panel feature. */
    setEnabled(enabled: boolean): void {
        if (this._enabled === enabled) {
            return;
        }
        this._enabled = enabled;

        if (!enabled) {
            this._removeAllPanels();
        }
    }

    /** Whether the info panel feature is currently enabled. */
    get enabled(): boolean {
        return this._enabled;
    }

    /**
     * Return the panel for the given code cell, creating and attaching
     * one if it does not already exist.  Returns `undefined` when the
     * feature is disabled or the cell is not a CodeCell.
     */
    ensurePanelForCell(cell: Cell): JvoxInfoPanelWidget | undefined {
        if (!this._enabled || !(cell instanceof CodeCell)) {
            return undefined;
        }

        const id = cell.model.id;
        console.debug(`Ensuring info panel for cell ${id}`);
        if (this._panels.has(id)) {
            return this._panels.get(id)!;
        }

        // add a new panel for this cell
        return this._attachPanel(cell);
    }

    /**
     * Convenience wrapper: ensure a panel exists for the currently
     * active cell and return it.
     */
    ensureActivePanel(): JvoxInfoPanelWidget | undefined {
        const cell = this._tracker.activeCell;
        if (!cell) {
            return undefined;
        }
        return this.ensurePanelForCell(cell);
    }

    /**
     * Retrieve the panel for a given cell without creating one.
     */
    getPanelForCell(cell: Cell): JvoxInfoPanelWidget | undefined {
        if (!(cell instanceof CodeCell)) {
            return undefined;
        }
        return this._panels.get(cell.model.id);
    }

    /**
     * Retrieve the panel for the currently active cell without creating one.
     */
    getActivePanel(): JvoxInfoPanelWidget | undefined {
        const cell = this._tracker.activeCell;
        if (!cell) {
            return undefined;
        }
        return this.getPanelForCell(cell);
    }

    /**
     * Open (ensure) the info panel for the currently active cell and
     * move keyboard focus to it.  Returns the panel, or `undefined`
     * if the feature is disabled or there is no active code cell.
     */
    openActivePanel(): JvoxInfoPanelWidget | undefined {
        const panel = this.ensureActivePanel();
        if (panel) {
            panel.node.focus();
        }
        return panel;
    }

    /**
     * Close (remove) the info panel for the currently active cell.
     * Returns `true` if a panel was removed, `false` otherwise.
     */
    closeActivePanel(): boolean {
        console.debug("JVoxInfoPanelManager: closeActivePanel called");
        const cell = this._tracker.activeCell;
        if (!cell || !(cell instanceof CodeCell)) {
            return false;
        }

        const id = cell.model.id;
        const panel = this._panels.get(id);
        if (!panel) {
            return false;
        }
        panel.detachFromCell();

        panel.dispose();
        this._panels.delete(id);
        return true;
    }

    /**
     * Register the open / close info-panel commands with JupyterLab.
     */
    registerInfoPanelCommands(
        app: JupyterFrontEnd,
        palette: ICommandPalette
    ): void {
        const { commands } = app;

        const openCmd = JVoxCommandRegistry.getCommandById('jvox:open-info-panel');
        if (openCmd) {
            commands.addCommand(openCmd.id, {
                label: openCmd.label,
                execute: () => this.openActivePanel()
            });
            app.commands.addKeyBinding({
                command: openCmd.id,
                keys: openCmd.hotkeys,
                selector: openCmd.selector
            });
            palette.addItem({ command: openCmd.id, category: 'JVox Operations' });
        }

        const closeCmd = JVoxCommandRegistry.getCommandById('jvox:close-info-panel');
        if (closeCmd) {
            commands.addCommand(closeCmd.id, {
                label: closeCmd.label,
                execute: () => this.closeActivePanel()
            });
            app.commands.addKeyBinding({
                command: closeCmd.id,
                keys: closeCmd.hotkeys,
                selector: closeCmd.selector
            });
            palette.addItem({ command: closeCmd.id, category: 'JVox Operations' });
        }
    }

    // ------------------------------------------------------------------
    // Private helpers
    // ------------------------------------------------------------------

    /** Remove all panels and their DOM traces. */
    private _removeAllPanels(): void {
        for (const [id, panel] of this._panels) {
            panel.dispose();
            this._panels.delete(id);
        }
    }

    /**
     * Hook into a notebook's cell list to clean up orphaned panels
     * when cells are removed.
     */
    private _hookNotebookForCleanup(notebook: {
        widgets: ReadonlyArray<Cell>;
        model: { cells: { changed: import('@lumino/signaling').ISignal<any, any> } } | null;
        modelChanged: import('@lumino/signaling').ISignal<any, void>;
    }): void {
        const cleanup = () => this._removeOrphanedPanels(notebook);

        if (notebook.model) {
            notebook.model.cells.changed.connect(cleanup, this);
        }

        notebook.modelChanged.connect(() => {
            if (notebook.model) {
                notebook.model.cells.changed.connect(cleanup, this);
            }
        }, this);
    }

    /**
     * Remove panels whose cells no longer exist in the notebook.
     */
    private _removeOrphanedPanels(notebook: {
        widgets: ReadonlyArray<Cell>;
    }): void {
        const activeCellIds = new Set<string>();
        for (const cell of notebook.widgets) {
            if (cell instanceof CodeCell) {
                activeCellIds.add(cell.model.id);
            }
        }

        for (const [id, panel] of this._panels) {
            if (!activeCellIds.has(id)) {
                panel.dispose();
                this._panels.delete(id);
            }
        }
    }

    /**
     * Attach a new info panel widget to a code cell.
     * The widget is inserted after the cell's input wrapper,
     * appearing below the code editor and above the output area.
     */
    private _attachPanel(cell: CodeCell): JvoxInfoPanelWidget {
        const id = cell.model.id;
        const panel = new JvoxInfoPanelWidget(id);
        this._panels.set(id, panel);

        panel.attachToCell(cell);

        return panel;
    }
}
