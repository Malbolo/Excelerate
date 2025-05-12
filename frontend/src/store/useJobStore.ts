import { create } from 'zustand';

interface JobState {
  isEditMode: boolean;
  canSaveJob: boolean;
  setIsEditMode: (isEditMode: boolean) => void;
  setCanSaveJob: (canSaveJob: boolean) => void;
  resetJob: () => void;
}

export const useJobStore = create<JobState>(set => ({
  isEditMode: false,
  canSaveJob: false,

  setIsEditMode: isEditMode => set({ isEditMode }),
  setCanSaveJob: canSaveJob => set({ canSaveJob }),
  resetJob: () => set({ isEditMode: false, canSaveJob: false }),
}));
