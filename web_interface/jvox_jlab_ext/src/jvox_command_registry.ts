// a central repository to manage commands and their hotkeys

export class JVoxCommandRegistry {
    public static commands = [
		{
            id: 'jvox:read-line-at-Cursor',
            label: 'Read the Line at Cursor',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt R'],
            hotkeys_Mac: ['Accel Shift R']
        },
        {
            id: 'jvox:read-last-error',
            label: 'Read Last Error',
            selector: '.jp-Notebook',
            hotkeys: ['Accel Alt E'],
            hotkeys_Mac: ['Accel Shift E']
        },
        {
            id: 'jvox:jump-to-last-error-column',
            label: 'Jump to the Line and Column of Last Error',
            selector: '.jp-Notebook',
            hotkeys: ['Accel Alt J'],
            hotkeys_Mac: ['Accel Shift J']
        },
        {
            id: 'jvox:goto-last-error-line',
            label: 'Goto the Line of Last Error',
            selector: '.jp-Notebook',
            hotkeys: ['Accel Alt G'],
            hotkeys_Mac: ['Accel Shift G']
        },
        {
            id: 'jvox:check-cell-syntax',
            label: 'Check the Syntax of Current Cell at Cursor', 
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt C'],
            hotkeys_Mac: ['Accel Shift C']
        },
        {
            id: 'jvox:verify-current-line',
            label: 'Check Current Cursor Line',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt V'],
            hotkeys_Mac: ['Accel Shift V']
        },
        {
            id: 'jvox:read-next-chunk',
            label: 'Read Next Chunk from Current Cursor Position',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt N'],
            hotkeys_Mac: ['Accel Shift N']
        },
        {
            id: 'jvox:read-previous-chunk',
            label: 'Read Previous Chunk from Current Cursor Position',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt P'],
            hotkeys_Mac: ['Accel Shift P']
        },
        {
            id: 'jvox:read-current-chunk',
            label: 'Read the Chunk at Current Cursor Position',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt K'],
            hotkeys_Mac: ['Accel Shift K']
        },
        {
            id: 'jvox:ai-code-explanation',
            label: 'AI-based code explanation of current line or current selection',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt A'],
            hotkeys_Mac: ['Accel Shift A']
        },
        {
            id: 'jvox:ai-code-nested-operation-explanation',
            label: 'AI-based explanation of the nested options of current line or current selection',
            selector: '.jp-Notebook.jp-mod-editMode',
            hotkeys: ['Accel Alt Q'],
            hotkeys_Mac: ['Alt Shift Q']
        },
    ];

    /**
     * Get the command object by its id.
     */
    public static getCommandById(id: string) {
        // Detect if the underlying OS is MacOS
        const isMacOS = typeof navigator !== 'undefined' && /Mac/.test(navigator.platform);
        console.log("JVox command registry: getCommandById: isMacOS = ", isMacOS);

        let command = this.commands.find(cmd => cmd.id === id);
        if (isMacOS && command?.hotkeys_Mac) {
            command.hotkeys = command.hotkeys_Mac;
        }
        return command;
    }
}