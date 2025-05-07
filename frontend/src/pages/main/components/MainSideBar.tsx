import { memo, useState } from 'react';

import Editor from '@monaco-editor/react';
import { ColumnDef } from '@tanstack/react-table';
import { DownloadIcon, Expand } from 'lucide-react';

import { useGetJobLogs } from '@/apis/agentMonitoring';
import DataTable from '@/components/DataTable';
import LLMGraph from '@/components/Graph/LLMGraph';
import Tabs from '@/components/Tabs';
import { DataFrame, DataFrameRow } from '@/types/dataframe';

import DataFrameModal from './DataFrameModal';

const BASE_URL = import.meta.env.VITE_BASE_URL;

interface MainSideBarProps {
  data: DataFrame | null;
  columns: ColumnDef<DataFrameRow>[];
  code: string;
  logId: string;
  downloadToken: string;
}

const MainSideBar = memo<MainSideBarProps>(
  ({ data, columns, code, logId, downloadToken }) => {
    const tabPanels = [
      <DataPanel
        key='data'
        data={data}
        columns={columns}
        downloadToken={downloadToken}
      />,
      <CodePanel key='code' code={code} />,
      <TracePanel key='trace' logId={logId} />,
    ];

    return (
      <div className='relative flex h-full w-full bg-[#F0F0F0] px-2 py-6'>
        <Tabs tabList={['Data', 'Code', 'Trace']} tabPanels={tabPanels} />
      </div>
    );
  },
);

MainSideBar.displayName = 'MainSideBar';

export default MainSideBar;

const DataPanel = memo<{
  data: DataFrame | null;
  columns: ColumnDef<DataFrameRow>[];
  downloadToken: string;
}>(({ data, columns, downloadToken }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);

  if (!data)
    return (
      <div className='border-border flex h-full items-center justify-center rounded-tl-md rounded-b-md border bg-white p-2'>
        No data
      </div>
    );

  return (
    <div className='flex h-[90vh] flex-col'>
      <DataTable columns={columns} data={data} />
      {downloadToken && (
        <a
          href={`${BASE_URL}/api/agent/download?token=${downloadToken}`}
          className='absolute right-1 bottom-2 z-10 cursor-pointer rounded-full bg-black p-3'
        >
          <DownloadIcon color='white' size={18} />
        </a>
      )}
      <div className='absolute bottom-2 left-1 z-10 cursor-pointer rounded-full border bg-white p-3'>
        <Expand
          color='black'
          size={18}
          onClick={() => {
            setIsModalOpen(true);
          }}
        />
      </div>
      <DataFrameModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        data={data}
        columns={columns}
      />
    </div>
  );
});

DataPanel.displayName = 'DataPanel';

const CodePanel: React.FC<{ code: string }> = ({ code }) => {
  if (!code)
    return (
      <div className='border-border grow rounded-tl-md rounded-b-md border bg-white py-2'>
        <div className='flex h-full items-center justify-center'>No code</div>
      </div>
    );

  return (
    <div className='border-border grow rounded-tl-md rounded-b-md border bg-white py-2'>
      <Editor
        defaultLanguage='python'
        defaultValue={code}
        options={{
          readOnly: true,
          domReadOnly: true,
          minimap: { enabled: false },
        }}
      />
    </div>
  );
};

const TracePanel: React.FC<{ logId: string }> = ({ logId }) => {
  const { data: logs } = useGetJobLogs(logId);

  if (!logId)
    return (
      <div className='border-border grow rounded-tl-md rounded-b-md border bg-white py-2'>
        <div className='flex h-full items-center justify-center'>No Log</div>
      </div>
    );

  return (
    <div className='border-border grow overflow-auto rounded-tl-md rounded-b-md border bg-white p-4'>
      <LLMGraph jobName='Current Job' logs={logs ?? []} />
    </div>
  );
};
