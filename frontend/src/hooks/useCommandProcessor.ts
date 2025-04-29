import { useState } from 'react';

import { TCommand } from '../types/job';

export const useCommandProcessor = (initialCommands: TCommand[] = []) => {
  const [commandList, setCommandList] = useState<TCommand[]>(initialCommands);

  const addCommand = (command: string) => {
    setCommandList(prev => [...prev, { title: command, status: 'pending' }]);
  };

  const editCommand = (oldCommand: string, newCommand: string) => {
    setCommandList(prev =>
      prev.map(cmd =>
        cmd.title === oldCommand ? { ...cmd, title: newCommand } : cmd,
      ),
    );
  };

  const deleteCommand = (command: string) => {
    setCommandList(prev => prev.filter(cmd => cmd.title !== command));
  };

  const processCommands = async () => {
    for (let i = 0; i < commandList.length; i++) {
      // Update current command to processing
      setCommandList(prev =>
        prev.map((cmd, idx) =>
          idx === i ? { ...cmd, status: 'processing' } : cmd,
        ),
      );

      // Wait for 1 second
      await new Promise(resolve => setTimeout(resolve, 1000));

      // Update current command to success
      setCommandList(prev =>
        prev.map((cmd, idx) =>
          idx === i ? { ...cmd, status: 'success' } : cmd,
        ),
      );
    }
  };

  return {
    commandList,
    addCommand,
    editCommand,
    deleteCommand,
    processCommands,
  };
};
