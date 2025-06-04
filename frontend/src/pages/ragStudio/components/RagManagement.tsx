import DocumentManagement from './DocumentManagement';
import { FileUpload } from './FileUpload';

const RagManagement = () => {
  return (
    <div className='l:w-1/3 flex h-full w-2/5 flex-col gap-4'>
      <section className='flex flex-col gap-4'>
        <h2 className='mt-0.5 text-lg font-bold'>Upload Documents</h2>
        <FileUpload />
      </section>

      <section className='flex flex-1 flex-col gap-4 overflow-hidden'>
        <h2 className='text-lg font-bold'>Document Management</h2>
        <DocumentManagement />
      </section>
    </div>
  );
};

export default RagManagement;
