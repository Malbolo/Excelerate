import { create } from 'zustand';

interface SourceState {
  sourceDataCommand: string;
  sourceDataUrl: string;
  sourceDataCode: string;

  setSourceDataCommand: (command: string) => void;
  setSourceDataUrl: (url: string) => void;
  setSourceDataCode: (code: string) => void;
  resetSource: () => void;
}

export const useSourceStore = create<SourceState>(set => ({
  sourceDataCommand: '',
  sourceDataUrl: '',
  sourceDataCode: '',

  setSourceDataCommand: command => set({ sourceDataCommand: command }),
  setSourceDataUrl: url => set({ sourceDataUrl: url }),
  setSourceDataCode: code => set({ sourceDataCode: code }),
  resetSource: () =>
    set({
      sourceDataCommand: '',
      sourceDataUrl: '',
      sourceDataCode: '',
    }),
}));
