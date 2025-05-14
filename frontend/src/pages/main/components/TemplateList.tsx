import { Settings } from 'lucide-react';
import { Link } from 'react-router-dom';

import { useGetUserInfoAPI } from '@/apis/auth';
import { useGetTemplates } from '@/apis/templates';
import { Button } from '@/components/ui/button';

const TemplateList = () => {
  const { data: userInfo } = useGetUserInfoAPI();
  const isAdmin = userInfo?.role === 'ADMIN';
  const { data: templates } = useGetTemplates();

  return (
    <section className='flex max-h-48 flex-1 flex-col gap-4'>
      <div className='flex items-center justify-between'>
        <p className='text-lg font-bold'>Template List</p>
        {isAdmin && (
          <Link to='/template-management'>
            <Button variant='ghost' className='h-6'>
              <Settings />
              Settings
            </Button>
          </Link>
        )}
      </div>
      <div className='card-gradient flex grow flex-col gap-2 overflow-y-auto rounded-xl border p-4'>
        <ul className='flex flex-col gap-2.5'>
          {templates.templates.map(template => (
            <li
              key={template}
              className='group hover:text-accent-foreground flex items-center gap-3 rounded-lg p-1'
            >
              <div className='bg-primary/80 h-1.5 w-1.5 rounded-full transition-all group-hover:scale-125' />
              {template}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};

export default TemplateList;
