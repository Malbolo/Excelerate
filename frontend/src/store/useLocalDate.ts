import { create } from 'zustand';

interface LocalDateState {
  locale: string;
  place: string;
  setLocale: (locale: string) => void;
  setPlace: (place: string) => void;
}

export const useLocalDate = create<LocalDateState>(set => ({
  locale: 'ko-KR',
  place: 'Asia/Seoul',
  setLocale: locale => set({ locale }),
  setPlace: place => set({ place }),
}));
