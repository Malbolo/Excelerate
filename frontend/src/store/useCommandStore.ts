import { create } from 'zustand';

import { TCommand, TCommandStatus } from '@/types/job';

interface CommandState {
  commandList: TCommand[];

  setCommandList: (commands: TCommand[]) => void;
  addCommand: (command: string) => void;
  deleteCommand: (index: number) => void;
  updateCommand: (index: number, newCommand: string) => void;
  updateCommandStatus: (index: number, status: TCommandStatus) => void;
  reorderCommands: (oldIndex: number, newIndex: number) => void;
  resetCommand: () => void;
}

export const useCommandStore = create<CommandState>(set => ({
  commandList: [],
  command: '',

  setCommandList: commands => set({ commandList: commands }),

  addCommand: command =>
    set(state => ({
      commandList: [
        ...state.commandList,
        { title: command, status: 'pending' },
      ],
    })),

  deleteCommand: index =>
    set(state => ({
      commandList: state.commandList
        .filter((_, i) => i !== index)
        .map(cmd => ({ ...cmd, status: 'pending' })),
    })),

  updateCommand: (index, newCommand) =>
    set(state => ({
      commandList: state.commandList.map((cmd, i) =>
        i === index
          ? { title: newCommand, status: 'pending' }
          : { ...cmd, status: 'pending' },
      ),
    })),

  updateCommandStatus: (index, status) =>
    set(state => ({
      commandList: state.commandList.map((cmd, i) =>
        i === index ? { ...cmd, status } : cmd,
      ),
    })),

  reorderCommands: (oldIndex: number, newIndex: number) =>
    set(state => {
      const newList = [...state.commandList];
      const [movedItem] = newList.splice(oldIndex, 1);
      newList.splice(newIndex, 0, movedItem);

      return {
        commandList: newList.map(cmd => ({ ...cmd, status: 'pending' })),
      };
    }),

  resetCommand: () =>
    set({
      commandList: [],
    }),
}));
