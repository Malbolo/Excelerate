import { useState } from 'react';

import { cn } from '@/lib/utils';

interface TabsProps {
  tabList: string[];
  tabPanels: React.ReactNode[];
}

const Tabs: React.FC<TabsProps> = ({ tabList, tabPanels }) => {
  const [activeTab, setActiveTab] = useState(tabList[0]);

  return (
    <div className='flex h-full w-full flex-col'>
      <div className='flex translate-y-[1px] self-end'>
        {tabList.map(tab => (
          <div
            onClick={() => setActiveTab(tab)}
            className={cn(
              'cursor-pointer rounded-t-md border px-2',
              activeTab === tab
                ? 'border-[#034EA2] bg-[#034EA2] text-white'
                : 'bg-white',
            )}
          >
            {tab}
          </div>
        ))}
      </div>
      {tabPanels[tabList.indexOf(activeTab)]}
    </div>
  );
};

export default Tabs;
