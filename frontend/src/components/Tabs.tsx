import { Suspense, useState } from 'react';

import { cn } from '@/lib/utils';

interface TabsProps {
  tabList: string[];
  tabPanels: React.ReactNode[];
}

const Tabs: React.FC<TabsProps> = ({ tabList, tabPanels }) => {
  const [activeTab, setActiveTab] = useState(tabList[0]);

  return (
    <div className='flex h-full w-full flex-col'>
      <div className='flex self-end'>
        {tabList.map(tab => (
          <div
            onClick={() => setActiveTab(tab)}
            className={cn(
              'cursor-pointer rounded-t-md border-t border-r border-l px-2',
              activeTab === tab
                ? 'bg-primary border-primary text-white'
                : 'bg-white',
            )}
          >
            {tab}
          </div>
        ))}
      </div>

      <div className='card-gradient h-full overflow-hidden rounded-l-lg rounded-br-lg border'>
        <Suspense
          fallback={
            <div className='flex h-full items-center justify-center'>
              Loading...
            </div>
          }
        >
          {tabPanels[tabList.indexOf(activeTab)]}
        </Suspense>
      </div>
    </div>
  );
};

export default Tabs;
