import { create } from 'zustand';

import { TJobType } from '@/types/agent';

interface JobState {
  id?: string;
  title: string;
  description: string;
  type?: TJobType;
  isEditMode: boolean;
  canSaveJob: boolean;
  setId: (id: string) => void;
  setTitle: (title: string) => void;
  setDescription: (description: string) => void;
  setType: (type: TJobType) => void;
  setIsEditMode: (isEditMode: boolean) => void;
  setCanSaveJob: (canSaveJob: boolean) => void;
  resetJob: () => void;
}

export const useJobStore = create<JobState>(set => ({
  id: '',
  title: '',
  description: '',
  type: undefined,
  isEditMode: false,
  canSaveJob: false,
  setId: id => set({ id }),
  setTitle: title => set({ title }),
  setDescription: description => set({ description }),
  setType: type => set({ type }),
  setIsEditMode: isEditMode => set({ isEditMode }),
  setCanSaveJob: canSaveJob => set({ canSaveJob }),
  resetJob: () => set({ isEditMode: false, canSaveJob: false }),
}));
