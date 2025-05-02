import StatusIcon from '@/components/StatusIcon';
import { cn } from '@/lib/utils';
import { Command } from '@/types/scheduler';

interface CommandItemProps {
  command: Command;
  isFirst: boolean;
  isLast: boolean;
}

const CommandItem = ({ command }: CommandItemProps) => {
  const getStatusColor = () => {
    switch (command.commandStatus) {
      case 'success':
        return 'text-green-700';
      case 'error':
        return 'text-red-700';
      case 'pending':
        return 'text-yellow-700';
      default:
        return 'text-gray-700';
    }
  };

  return (
    <div
      className={cn(
        'flex items-center space-x-2 rounded px-2 py-1',
        command.commandStatus === 'success' ? 'bg-green-50/50' : '',
        command.commandStatus === 'error' ? 'bg-red-50/50' : '',
        command.commandStatus === 'pending' ? 'bg-yellow-50/50' : '',
      )}
    >
      <StatusIcon status={command.commandStatus} />
      <span className={cn('text-sm', getStatusColor())}>
        {command.commandTitle}
      </span>
    </div>
  );
};

export default CommandItem;
