import { useState } from 'react';

import { MousePointerClick } from 'lucide-react';

import LLMGraph from '@/components/Graph/LLMGraph';
import { Log } from '@/types/agent';

import MetadataPanel from './MetadataPanel';
import RunPanel from './RunPanel';

interface AgentCallDetailProps {
  logs: Log[];
}

const AgentCallDetail = ({ logs }: AgentCallDetailProps) => {
  const [selectedLog, setSelectedLog] = useState<Log | null>(null);
  const handleClickLog = (log: Log) => {
    setSelectedLog(log);
  };

  return (
    <div className='@container/agent-call-detail h-full w-full overflow-clip'>
      <div className='flex h-full w-full flex-col divide-y'>
        {selectedLog && <p className='text-accent-foreground px-6 py-4 text-xs font-bold'>{selectedLog.name}</p>}
        <div className='flex h-full w-full flex-col gap-6 @4xl/agent-call-detail:flex-row'>
          <section className='p-4'>
            {logs.length > 0 && <LLMGraph jobName='Current Job' logs={logs} onLogClick={handleClickLog} />}
          </section>
          <section className='flex-1 overflow-x-clip overflow-y-auto border-t pt-4 @4xl/agent-call-detail:border-t-0 @4xl/agent-call-detail:border-l'>
            {selectedLog ? (
              <>
                <RunPanel input={selectedLog ? selectedLog.input : []} output={selectedLog ? selectedLog.output : []} />
                <MetadataPanel metadata={selectedLog ? selectedLog.metadata : {}} />
              </>
            ) : (
              <div className='flex h-full flex-col items-center justify-center gap-2'>
                <MousePointerClick size={20} className='text-accent-foreground' />
                <p className='text-sm'>Select a node from the graph to view details</p>
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  );
};

export default AgentCallDetail;
