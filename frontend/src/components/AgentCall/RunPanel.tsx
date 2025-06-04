import { Badge } from '@/components/ui/badge';
import { Log, LogMessage } from '@/types/agent';

interface MessageItemProps {
  message: LogMessage;
}

const MessageItem = ({ message }: MessageItemProps) => {
  return (
    <div className='flex flex-col gap-2'>
      <div className='flex items-center gap-2'>
        <Badge variant='secondary' className='font-medium'>
          {message.role}
        </Badge>
      </div>
      <div className='ml-4 rounded-md border bg-slate-50/50 p-4'>
        <p className='text-xs break-words whitespace-pre-wrap text-gray-600'>{message.message}</p>
      </div>
    </div>
  );
};

const RunPanel = ({ input, output }: Pick<Log, 'input' | 'output'>) => {
  if ((!input || input.length === 0) && (!output || output.length === 0)) {
    return (
      <div className='flex items-center justify-center rounded-tl-md rounded-b-md'>
        <p className='text-sm text-gray-500'>No data available</p>
      </div>
    );
  }

  return (
    <div className='flex overflow-y-auto rounded-tl-md rounded-b-md'>
      <div className='flex w-full flex-col gap-4 px-4'>
        {input && input.length > 0 && (
          <div className='flex flex-col gap-4'>
            <div className='flex items-center gap-2'>
              <Badge variant='outline' className='font-medium'>
                Input
              </Badge>
            </div>
            <div className='ml-4 flex flex-col gap-4 border-l border-gray-200 pl-4'>
              {input.map((message, index) => (
                <MessageItem key={`input-${index}`} message={message} />
              ))}
            </div>
          </div>
        )}

        {output && output.length > 0 && (
          <div className='flex flex-col gap-4'>
            <div className='flex items-center gap-2'>
              <Badge variant='outline' className='font-medium'>
                Output
              </Badge>
            </div>
            <div className='ml-4 flex flex-col gap-4 border-l border-gray-200 pl-4'>
              {output.map((message, index) => (
                <MessageItem key={`output-${index}`} message={message} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RunPanel;
