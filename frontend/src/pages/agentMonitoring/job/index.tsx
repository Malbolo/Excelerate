import { useState } from 'react';

import LLMGraph from '@/components/Graph/LLMGraph';
import Tabs from '@/components/Tabs';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Badge } from '@/components/ui/badge';
import { MGraphWithSubEvents } from '@/mocks/datas/graph';
import { TLog } from '@/types/agent';

const JobAgentMonitoringPage: React.FC = () => {
  const [logs] = useState<TLog[]>(MGraphWithSubEvents);

  return (
    <div className='flex h-screen w-full'>
      <section className='h-full w-[400px] overflow-y-auto bg-[#F0F0F0] p-6'>
        <LLMGraph jobName='job name' logs={logs} />
      </section>
      <section className='h-full flex-1 p-4'>
        <Tabs
          tabList={['Run', 'Metadata']}
          // TODO: 추후 특정 Chain 클릭 시 해당 데이터만 보여줄 수 있도록 수정 (현재는 index=0으로 고정)
          tabPanels={[
            <RunPanel input={logs[0].input} output={logs[0].output} />,
            <MetadataPanel metadata={logs[0].metadata} />,
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
