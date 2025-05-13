import { useState } from 'react';

import { ArrowLeftIcon } from 'lucide-react';
import { useParams } from 'react-router-dom';

import { useGetJobLogs } from '@/apis/agentMonitoring';
import LLMGraph from '@/components/Graph/LLMGraph';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import useInternalRouter from '@/hooks/useInternalRouter';
import Tabs from '@/pages/main/components/Tabs';
import { Log, LogMessage, LogMetadata } from '@/types/agent';

// 컴포넌트 분리가 어려워 컴포넌트 분리 추후 진행
const JobAgentMonitoringPage = () => {
  const { jobId } = useParams() as { jobId: string };
  const { goBack } = useInternalRouter();

  const { data: logs } = useGetJobLogs(jobId);

  const [selectedLog, setSelectedLog] = useState<Log | null>(null);

  const handleClickLog = (log: Log) => {
    setSelectedLog(log);
  };

  return (
    <div className='flex h-screen w-full'>
      <section className='h-full min-w-[400px] overflow-y-auto bg-[#F0F0F0] p-6'>
        <div className='mb-4'>
          <Button
            variant='ghost'
            size='sm'
            onClick={goBack}
            className='flex items-center gap-2'
          >
            <ArrowLeftIcon className='h-4 w-4' />
            Back
          </Button>
        </div>
        <LLMGraph jobName='job name' logs={logs} onLogClick={handleClickLog} />
      </section>
      <section className='h-full flex-1 p-4'>
        <Tabs
          tabList={['Run', 'Metadata']}
          tabPanels={[
            <RunPanel
              input={selectedLog ? selectedLog.input : []}
              output={selectedLog ? selectedLog.output : []}
            />,
            <MetadataPanel
              metadata={selectedLog ? selectedLog.metadata : {}}
            />,
          ]}
        />
      </section>
    </div>
  );
};

export default JobAgentMonitoringPage;

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
      <div className='ml-4 rounded-md bg-gray-50 p-4'>
        <p className='text-sm whitespace-pre-wrap text-gray-600'>
          {message.message}
        </p>
      </div>
    </div>
  );
};

const RunPanel = ({ input, output }: Pick<Log, 'input' | 'output'>) => {
  if ((!input || input.length === 0) && (!output || output.length === 0)) {
    return (
      <div className='flex h-full items-center justify-center rounded-tl-md rounded-b-md border bg-white p-2'>
        <p className='text-sm text-gray-500'>No data available</p>
      </div>
    );
  }

  return (
    <div className='flex h-full overflow-y-auto rounded-tl-md rounded-b-md border bg-white p-2'>
      <div className='flex w-full flex-col gap-4 px-4 py-5'>
        {input && input.length > 0 && (
          <div className='flex flex-col gap-4'>
            <div className='flex items-center gap-2'>
              <Badge variant='outline' className='font-medium'>
                Input
              </Badge>
            </div>
            <div className='ml-4 flex flex-col gap-4 border-l-2 border-gray-200 pl-4'>
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
            <div className='ml-4 flex flex-col gap-4 border-l-2 border-gray-200 pl-4'>
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

interface MetadataItemProps {
  label: string;
  value: LogMetadata | string | number | null;
  depth?: number;
}

const MetadataItem = ({ label, value, depth = 0 }: MetadataItemProps) => {
  if (value === null) return null;

  if (typeof value === 'object') {
    return (
      <div className='flex flex-col gap-2'>
        <div className='flex items-center gap-2'>
          <Badge variant='outline' className='font-medium'>
            {label}
          </Badge>
        </div>
        <div className='ml-4 flex flex-col gap-2 border-l-2 border-gray-200 pl-4'>
          {Object.entries(value).map(([key, val]) => (
            <MetadataItem key={key} label={key} value={val} depth={depth + 1} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='flex items-center gap-2'>
      <Badge variant='outline' className='font-medium'>
        {label}
      </Badge>
      <span className='text-sm text-gray-600'>{String(value)}</span>
    </div>
  );
};

const MetadataPanel = ({ metadata }: Pick<Log, 'metadata'>) => {
  if (!metadata || Object.keys(metadata).length === 0) {
    return (
      <div className='flex h-full items-center justify-center rounded-tl-md rounded-b-md border bg-white p-2'>
        <p className='text-sm text-gray-500'>No metadata available</p>
      </div>
    );
  }

  return (
    <div className='flex h-full overflow-y-auto rounded-tl-md rounded-b-md border bg-white p-2'>
      <div className='flex flex-col gap-4 px-4 py-5'>
        {Object.entries(metadata).map(([key, value]) => (
          <MetadataItem key={key} label={key} value={value} />
        ))}
      </div>
    </div>
  );
};
