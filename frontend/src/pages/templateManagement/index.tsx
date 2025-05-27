import { ArrowLeftIcon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import useInternalRouter from '@/hooks/useInternalRouter';

import CreateTemplateForm from './components/CreateTemplateForm';
import TemplateList from './components/TemplateList';

const TemplateManagementPage = () => {
  const { goBack } = useInternalRouter();

  return (
    <section className='bg-gradient flex h-screen flex-1 flex-col overflow-hidden p-8'>
      <div className='mb-6 flex items-center gap-4'>
        <Button variant='ghost' size='sm' onClick={goBack} className='flex items-center gap-2'>
          <ArrowLeftIcon className='h-4 w-4' />
          Back
        </Button>
      </div>
      <CreateTemplateForm />
      <TemplateList />
    </section>
  );
};
export default TemplateManagementPage;
