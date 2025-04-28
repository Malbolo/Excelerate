import { AlertCircleIcon } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Command } from '@/types/scheduler';

interface CommandItemProps {
  command: Command;
  isFirst: boolean;
  isLast: boolean;
}

// todo: 더미데이터이기에 실제 변경 예정
const CommandItem: React.FC<CommandItemProps> = ({
  command,
  isFirst,
  isLast,
}) => {
  const getStatusStyles = () => {
    switch (command.commandStatus) {
      case 'success':
        return 'border-green-500 bg-green-50';
      case 'error':
        return 'border-red-500 bg-red-50 text-red-700';
      default:
        return 'border-gray-300 bg-gray-50';
    }
  };

  return (
    <div className='relative px-4'>
      {!isFirst && (
        <div className='absolute top-0 left-6 h-1/2 w-0.5 bg-gray-300' />
      )}
      {!isLast && (
        <div className='absolute bottom-0 left-6 h-1/2 w-0.5 bg-gray-300' />
      )}

      <div
        className={cn(
          `relative z-10 flex items-center space-x-3 rounded-lg border-2 p-3 shadow-sm`,
          getStatusStyles(),
        )}
      >
        <span className='flex-1'>{command.commandTitle}</span>
        {command.commandStatus === 'error' && (
          <AlertCircleIcon className='h-6 w-6 text-red-500' />
        )}
      </div>
    </div>
  );
};

export default CommandItem;
