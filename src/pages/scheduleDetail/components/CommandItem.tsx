import { Command } from '@/types/scheduler';

interface CommandItemProps {
  command: Command;
  isFirst: boolean;
  isLast: boolean;
}

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
        className={`relative z-10 flex items-center space-x-3 rounded-lg border-2 p-3 shadow-sm ${getStatusStyles()}`}
      >
        <span className='flex-1'>{command.commandTitle}</span>
        {command.commandStatus === 'error' && (
          <svg
            xmlns='http://www.w3.org/2000/svg'
            className='h-6 w-6 text-red-500'
            fill='none'
            viewBox='0 0 24 24'
            stroke='currentColor'
            strokeWidth={2}
          >
            <path
              strokeLinecap='round'
              strokeLinejoin='round'
              d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
            />
          </svg>
        )}
      </div>
    </div>
  );
};

export default CommandItem;
