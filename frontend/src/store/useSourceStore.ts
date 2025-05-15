import { create } from 'zustand';

interface SourceState {
  sourceDataCommand: string;
  sourceDataUrl: string;
  sourceDataCode: string;
  sourceParams: Record<string, string>;

  setSourceDataCode: (code: string) => void;

  setSourceDataCommand: (command: string) => void;
  setSourceDataUrl: (url: string) => void;
  setSourceParams: (params: Record<string, string>) => void;
  resetSource: () => void;
}

export const useSourceStore = create<SourceState>(set => ({
  sourceDataCommand: '',
  sourceDataUrl: '',
  sourceDataCode: '',

  setSourceDataCommand: command => set({ sourceDataCommand: command }),
  setSourceDataUrl: url => set({ sourceDataUrl: url }),
  setSourceDataCode: code => set({ sourceDataCode: code }),
  sourceParams: {},

  setSourceParams: params => set({ sourceParams: params }),
  resetSource: () =>
    set({
      sourceDataCommand: '',
      sourceDataUrl: '',
      sourceDataCode: '',
      sourceParams: {},
    }),
}));
