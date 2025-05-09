import { useState } from 'react';

import { MTemplates } from '@/mocks/datas/template';

const TemplateList: React.FC = () => {
  const [templates] = useState<string[]>(MTemplates);

  return (
    <section className='flex max-h-48 flex-1 flex-col gap-4'>
      <p className='text-lg font-bold'>Template List</p>
      <div className='card-gradient flex grow flex-col gap-2 overflow-y-auto rounded-xl border p-4'>
        <ul className='flex flex-col gap-2.5'>
          {templates.map(template => (
            <li
              key={template}
              className='group hover:text-accent-foreground flex items-center gap-3 rounded-lg p-1'
            >
              <div className='bg-primary/80 group-hover:bg-primary h-1.5 w-1.5 rounded-full transition-all group-hover:scale-125' />
              {template}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};

export default TemplateList;
