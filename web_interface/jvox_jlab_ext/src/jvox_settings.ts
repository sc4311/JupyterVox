/**
 * JVox Settings Manager
 *
 * Centralises all JupyterLab user settings for the jvox-jlab-ext extension.
 * Other modules can import the singleton and read current values at any time.
 */

import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { ISignal, Signal } from '@lumino/signaling';

/** The two AI backends currently supported. */
export type AiClientType = 'ollama' | 'gemini';

/**
 * Manages loading, caching, and change-notification for all JVox settings.
 */
export class JVoxSettings {
    private _readingRate: number = 1.5;
    private _aiClient: AiClientType = 'ollama';
    private _geminiApiKey: string = '';

    /** Emitted whenever any setting value changes. */
    private _changed = new Signal<JVoxSettings, void>(this);

    get changed(): ISignal<JVoxSettings, void> {
        return this._changed;
    }

    // ── Accessors ──────────────────────────────────────────────

    get readingRate(): number {
        return this._readingRate;
    }

    get aiClient(): AiClientType {
        return this._aiClient;
    }

    get geminiApiKey(): string {
        return this._geminiApiKey;
    }

    // ── Initialisation ─────────────────────────────────────────

    /**
     * Load settings from the registry and subscribe to future changes.
     *
     * @param registry  The JupyterLab setting registry.
     * @param pluginId  The extension plugin id (e.g. 'jvox-jlab-ext:plugin').
     */
    async load(registry: ISettingRegistry, pluginId: string): Promise<void> {
        const settings = await registry.load(pluginId);
        this._applySettings(settings);

        settings.changed.connect(() => {
            this._applySettings(settings);
        });
    }

    // ── Internal ───────────────────────────────────────────────

    private _applySettings(settings: ISettingRegistry.ISettings): void {
        this._readingRate = settings.get('reading_rate').composite as number;
        this._aiClient = settings.get('ai_client').composite as AiClientType;
        this._geminiApiKey = settings.get('gemini_api_key').composite as string;

        console.log(
            `JVox settings applied – rate: ${this._readingRate}, ` +
            `ai_client: ${this._aiClient}, ` +
            `gemini_api_key: ${this._geminiApiKey ? '(set)' : '(empty)'}`
        );

        this._changed.emit(void 0);
    }
}
