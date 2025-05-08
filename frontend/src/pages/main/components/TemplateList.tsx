import { useState } from 'react';

import { MTemplates } from '@/mocks/datas/template';

const TemplateList: React.FC = () => {
  const [templates] = useState<string[]>(MTemplates);

  return (
    <section className='flex max-h-48 flex-1 flex-col gap-4'>
      <p className='text-lg font-bold text-gray-900'>Template List</p>
      <div className='flex grow flex-col gap-2 overflow-y-auto rounded-xl border border-[#E5E7EB] bg-gradient-to-b from-white to-[#F8FAFF] p-4 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-[#034EA2]/30 hover:[&::-webkit-scrollbar-thumb]:bg-[#034EA2]/50 [&::-webkit-scrollbar-track]:rounded-full [&::-webkit-scrollbar-track]:bg-gray-100'>
        <ul className='flex flex-col gap-2.5'>
          {templates.map(template => (
            <li
              key={template}
              className='group flex items-center gap-3 rounded-lg border border-[#E5E7EB] bg-white px-4 py-2.5 text-gray-700 transition-all hover:border-[#034EA2]/30 hover:bg-[#F0F7FF] hover:text-[#034EA2] hover:shadow-[0_4px_12px_rgba(3,78,162,0.12)]'
            >
              <div className='h-1.5 w-1.5 rounded-full bg-[#034EA2]/30 transition-all group-hover:scale-125 group-hover:bg-[#034EA2]/50' />
              {template}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};

export default TemplateList;
