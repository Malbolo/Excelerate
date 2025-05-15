import { memo, useState } from 'react';

import Editor from '@monaco-editor/react';
import { ColumnDef } from '@tanstack/react-table';
import { DownloadIcon, Expand, TriangleAlert } from 'lucide-react';

import { BASE_URL } from '@/constant/baseURL';
import AgentCallDetail from '@/pages/agentMonitoring/components/AgentCallDetail';
import Tabs from '@/pages/main/components/Tabs';
import { useJobResultStore } from '@/store/useJobResultStore';
import { useStreamStore } from '@/store/useStreamStore';
import { DataFrame, DataFrameRow } from '@/types/dataframe';
import { ErrorMessage } from '@/types/job';

import DataTable from './DataTable';
import ExpandModal from './ExpandModal';

const MainSideBar = memo(() => {
  const { dataframe, columns, code, downloadToken, errorMsg } =
    useJobResultStore();

  const tabPanels = [
    <DataPanel
      key='data'
      data={dataframe}
      columns={columns}
      downloadToken={downloadToken}
    />,
    <CodePanel key='code' code={code} errorMsg={errorMsg} />,
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
      <ExpandModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <DataTable columns={columns} data={data} />
      </ExpandModal>
    </div>
  );
});

DataPanel.displayName = 'DataPanel';

const CodePanel: React.FC<{
  code: string;
  errorMsg: ErrorMessage | null;
}> = ({ code, errorMsg }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  if (!code)
    return (
      <div className='flex h-full items-center justify-center'>No code</div>
    );

  return (
    <div className='h-full py-2'>
      {errorMsg && (
        <div className='text-destructive bg-destructive/10 mx-2 mb-4 flex items-center gap-2 rounded-lg p-2 px-4'>
          <TriangleAlert className='h-4 w-4 shrink-0' />
          <p className='text-sm'>{errorMsg.message}</p>
        </div>
      )}
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
      <div className='absolute bottom-2 left-1 z-10 cursor-pointer rounded-full border bg-white p-3'>
        <Expand
          color='#374151'
          size={18}
          onClick={() => {
            setIsModalOpen(true);
          }}
        />
      </div>
      <ExpandModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
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
      </ExpandModal>
    </div>
  );
};

const TracePanel: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { logs } = useStreamStore();

  if (!logs || logs.length === 0)
    return (
      <div className='flex h-full items-center justify-center'>No Log</div>
    );

  return (
    <div className='h-full'>
      <AgentCallDetail logs={logs} />
      <div className='absolute bottom-2 left-1 z-10 cursor-pointer rounded-full border bg-white p-3'>
        <Expand
          color='#374151'
          size={18}
          onClick={() => {
            setIsModalOpen(true);
          }}
        />
      </div>
      <ExpandModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <AgentCallDetail logs={logs} />
      </ExpandModal>
    </div>
  );
};
