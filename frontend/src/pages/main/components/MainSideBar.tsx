import { memo, useState } from 'react';

import Editor from '@monaco-editor/react';
import { ColumnDef } from '@tanstack/react-table';
import { DownloadIcon, Expand } from 'lucide-react';

import DataTable from '@/components/DataTable';
import LLMGraph from '@/components/Graph/LLMGraph';
import Tabs from '@/components/Tabs';
import { useJobResultStore } from '@/store/useJobResultStore';
import { useStreamStore } from '@/store/useStreamStore';
import { DataFrame, DataFrameRow } from '@/types/dataframe';

import DataFrameModal from './DataFrameModal';

const BASE_URL = import.meta.env.VITE_BASE_URL;

const MainSideBar = memo(() => {
  const { dataframe, columns, code, downloadToken } = useJobResultStore();

  const tabPanels = [
    <DataPanel
      key='data'
      data={dataframe}
      columns={columns}
      downloadToken={downloadToken}
    />,
    <CodePanel key='code' code={code} />,
    <TracePanel key='trace' />,
  ];

  return (
    <div className='relative flex h-full w-full border-l bg-[#FAFCFF] px-2 py-6'>
      <Tabs tabList={['Data', 'Code', 'Trace']} tabPanels={tabPanels} />
    </div>
  );
});

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
      <div className='flex h-full items-center justify-center'>No data</div>
    );

  return (
    <div className='flex h-[90vh] flex-col'>
      <DataTable columns={columns} data={data} />
      {downloadToken && (
        <a
          href={`${BASE_URL}/api/agent/download?token=${downloadToken}`}
          className='bg-primary border-primary absolute right-1 bottom-2 z-10 cursor-pointer rounded-full border p-3'
        >
          <DownloadIcon color='white' size={18} />
        </a>
      )}
      <div className='absolute bottom-2 left-1 z-10 cursor-pointer rounded-full border bg-white p-3'>
        <Expand
          color='#374151'
          size={18}
          onClick={() => {
            setIsModalOpen(true);
          }}
        />
      </div>
      <DataFrameModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </div>
  );
});

DataPanel.displayName = 'DataPanel';

const CodePanel: React.FC<{ code: string }> = ({ code }) => {
  if (!code)
    return (
      <div className='flex h-full items-center justify-center'>No code</div>
    );

  return (
    <div className='h-full py-2'>
      <Editor
        key={code}
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

const TracePanel: React.FC = () => {
  const { logs } = useStreamStore();

  if (!logs || logs.length === 0)
    return (
      <div className='flex h-full items-center justify-center'>No Log</div>
    );

  return (
    <div className='h-full grow overflow-auto p-4'>
      <LLMGraph jobName='Current Job' logs={logs ?? []} />
    </div>
  );
};
