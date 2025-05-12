import { create } from 'zustand';

interface SourceState {
  sourceDataCommand: string;
  sourceDataUrl: string;

  setSourceDataCommand: (command: string) => void;
  setSourceDataUrl: (url: string) => void;
  resetSource: () => void;
}

export const useSourceStore = create<SourceState>(set => ({
  sourceDataCommand: '',
  sourceDataUrl: '',

  setSourceDataCommand: command => set({ sourceDataCommand: command }),
  setSourceDataUrl: url => set({ sourceDataUrl: url }),
  resetSource: () =>
    set({
      sourceDataCommand: '',
      sourceDataUrl: '',
    }),
}));
