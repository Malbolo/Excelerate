import { useState } from 'react';

import { useParams } from 'react-router-dom';

import { useGetJobLogs } from '@/apis/agentMonitoring';
import LLMGraph from '@/components/Graph/LLMGraph';
import Tabs from '@/components/Tabs';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';
import { TLog } from '@/types/agent';

const JobAgentMonitoringPage: React.FC = () => {
  const { jobId } = useParams() as { jobId: string };

  const { data: logs } = useGetJobLogs(jobId);

  const [selectedLog, setSelectedLog] = useState<TLog>(logs[0]);

  const handleClickLog = (log: TLog) => {
    setSelectedLog(log);
  };

  return (
    <div className='flex h-screen w-full'>
      <section className='h-full w-[400px] overflow-y-auto bg-[#F0F0F0] p-6'>
        <LLMGraph jobName='job name' logs={logs} onLogClick={handleClickLog} />
      </section>
      <section className='h-full flex-1 p-4'>
        <Tabs
          tabList={['Run', 'Metadata']}
          tabPanels={[
            <RunPanel input={selectedLog.input} output={selectedLog.output} />,
            <MetadataPanel metadata={selectedLog.metadata} />,
          ]}
        />
      </section>
    </div>
  );
};

export default JobAgentMonitoringPage;

interface RunPanelProps {
  input: string;
  output: string;
}

const RunPanel: React.FC<RunPanelProps> = ({ input, output }) => {
  return (
    <div className='border-border flex h-full rounded-tl-md rounded-b-md border bg-white'>
      <div className='w-full px-6 py-4'>
        <Accordion type='multiple' defaultValue={['input', 'output']}>
          <AccordionItem value='input'>
            <AccordionTrigger>Input</AccordionTrigger>
            <AccordionContent>{input}</AccordionContent>
          </AccordionItem>
          <AccordionItem value='output'>
            <AccordionTrigger>Output</AccordionTrigger>
            <AccordionContent>{output}</AccordionContent>
          </AccordionItem>
        </Accordion>
      </div>
    </div>
  );
};

interface MetadataPanelProps {
  metadata: Record<string, string>;
}

const MetadataPanel: React.FC<MetadataPanelProps> = ({ metadata }) => {
  return (
    <div className='border-border flex h-full rounded-tl-md rounded-b-md border bg-white p-2'>
      <div className='flex flex-col gap-2 px-4 py-5'>
        {Object.entries(metadata).map(([key, value]) => (
          <div key={key} className='flex gap-2'>
            <Badge className='font-bold'>{key}</Badge>
            <span className='text-sm'>{value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
