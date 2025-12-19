import { create } from 'zustand';
import { getSettings, saveSettings } from '../services/api';
import type { Settings, Language } from '../types';

interface SettingsState extends Settings {
  isLoading: boolean;
  isLoaded: boolean;
  load: () => Promise<void>;
  save: (settings: Partial<Settings>) => Promise<boolean>;
  setApiKey: (key: string) => void;
  setBaseUrl: (url: string) => void;
  setDefaultModel: (model: string) => void;
  setUseStream: (useStream: boolean) => void;
  setLanguage: (language: Language) => void;
}

export const useSettingsStore = create<SettingsState>()((set, get) => ({
  apiKey: '',
  baseUrl: 'https://api.openai.com',
  defaultModel: 'claude-sonnet-4-5-20250929',
  useStream: false,
  language: 'cn',
  isLoading: false,
  isLoaded: false,

  load: async () => {
    if (get().isLoaded) return;
    
    set({ isLoading: true });
    try {
      const settings = await getSettings();
      set({ 
        ...settings, 
        language: settings.language || 'cn',
        isLoading: false, 
        isLoaded: true 
      });
    } catch {
      set({ isLoading: false, isLoaded: true });
    }
  },

  save: async (newSettings) => {
    const current = get();
    const settings: Settings = {
      apiKey: newSettings.apiKey ?? current.apiKey,
      baseUrl: newSettings.baseUrl ?? current.baseUrl,
      defaultModel: newSettings.defaultModel ?? current.defaultModel,
      useStream: newSettings.useStream ?? current.useStream,
      language: newSettings.language ?? current.language,
    };
    
    try {
      await saveSettings(settings);
      set(settings);
      return true;
    } catch {
      return false;
    }
  },

  setApiKey: (key) => set({ apiKey: key }),
  setBaseUrl: (url) => set({ baseUrl: url }),
  setDefaultModel: (model) => set({ defaultModel: model }),
  setUseStream: (useStream) => set({ useStream }),
  setLanguage: (language) => set({ language }),
}));
