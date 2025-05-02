import Tabs from '@/components/Tabs';

const JobAgentMonitoringPage: React.FC = () => {
  return (
    <div className='flex h-screen w-full'>
      <section className='h-full w-[400px] bg-[#F0F0F0]'></section>
      <section className='h-full flex-1 p-4'>
        <Tabs
          tabList={['Run', 'Metadata']}
          tabPanels={[<RunPanel />, <MetadataPanel />]}
        />
      </section>
    </div>
  );
};

export default JobAgentMonitoringPage;

const RunPanel: React.FC = () => {
  return (
    <div className='border-border flex h-full items-center justify-center rounded-tl-md rounded-b-md border bg-white p-2'>
      RunPanel
    </div>
  );
};

const MetadataPanel: React.FC = () => {
  return (
    <div className='border-border flex h-full items-center justify-center rounded-tl-md rounded-b-md border bg-white p-2'>
      MetadataPanel
    </div>
  );
};
