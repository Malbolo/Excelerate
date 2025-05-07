import { memo, useMemo } from 'react';

import Editor from '@monaco-editor/react';
import { ColumnDef } from '@tanstack/react-table';
import { DownloadIcon } from 'lucide-react';

import DataTable from '@/components/DataTable';
import Tabs from '@/components/Tabs';
import { DataFrame, DataFrameRow } from '@/types/dataframe';

interface MainSideBarProps {
  data: DataFrame | null;
  columns: ColumnDef<DataFrameRow>[];
  code: string;
  trace: string;
}

const MainSideBar = memo<MainSideBarProps>(({ data, columns, code, trace }) => {
  const tabPanels = useMemo(
    () => [
      <DataPanel key='data' data={data} columns={columns} />,
      <CodePanel key='code' code={code} />,
      <TracePanel key='trace' trace={trace} />,
    ],
    [data, columns, code, trace],
  );

  return (
    <div className='relative flex h-full w-full bg-[#F0F0F0] px-2 py-6'>
      <Tabs tabList={['Data', 'Code', 'Trace']} tabPanels={tabPanels} />
    </div>
  );
});

MainSideBar.displayName = 'MainSideBar';

export default MainSideBar;

const DataPanel = memo<{
  data: DataFrame | null;
  columns: ColumnDef<DataFrameRow>[];
}>(({ data, columns }) => {
  const memoizedColumns = useMemo(() => columns, [columns]);
  const memoizedData = useMemo(() => data, [data]);

  if (!memoizedData)
    return (
      <div className='border-border flex h-full items-center justify-center rounded-tl-md rounded-b-md border bg-white p-2'>
        No data
      </div>
    );

  return (
    <div className='flex h-[90vh] flex-col'>
      <DataTable columns={memoizedColumns} data={memoizedData} />
      <div className='absolute right-2 bottom-4 z-10 cursor-pointer rounded-full bg-black p-3'>
        <DownloadIcon color='white' size={18} />
      </div>
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

const TracePanel: React.FC<{ trace: string }> = ({ trace }) => {
  return (
    <div className='border-border grow rounded-tl-md rounded-b-md border bg-white'>
      {trace}
    </div>
  );
};
