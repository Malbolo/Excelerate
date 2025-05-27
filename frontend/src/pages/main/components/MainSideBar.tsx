import { memo } from 'react';

import Tabs from '@/pages/main/components/Tabs';
import { useJobResultStore } from '@/store/useJobResultStore';

import { CodePanel, DataPanel, TracePanel } from './SidePanel';

const MainSideBar = memo(() => {
  const { dataframe, columns, code, downloadToken, errorMsg } = useJobResultStore();

  const tabPanels = [
    <DataPanel key='data' data={dataframe} columns={columns} downloadToken={downloadToken} />,
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
