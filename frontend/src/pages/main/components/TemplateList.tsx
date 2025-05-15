import { useState } from 'react';

import { Download, Eye, Settings } from 'lucide-react';
import { Link } from 'react-router-dom';
import ClipLoader from 'react-spinners/ClipLoader';

import { useGetUserInfoAPI } from '@/apis/auth';
import { useGetTemplateImage, useGetTemplates } from '@/apis/templates';
import { Button } from '@/components/ui/button';

import ExpandModal from './ExpandModal';

const TemplateList = () => {
  const [openModal, setOpenModal] = useState(false);
  const [templateImage, setTemplateImage] = useState<string | null>(null);

  const { data: userInfo } = useGetUserInfoAPI();
  const isAdmin = userInfo?.role === 'ADMIN';
  const { data: templates } = useGetTemplates();

  const getTemplateImage = useGetTemplateImage();

  const handleGetTemplateImage = async (templateName: string) => {
    setOpenModal(true);
    const image = await getTemplateImage(templateName);
    setTemplateImage(image);
  };

  return (
    <section className='flex flex-1 flex-col justify-between gap-2'>
      {openModal && (
        <ExpandModal isOpen={openModal} onClose={() => setOpenModal(false)}>
          {templateImage ? (
            <img src={templateImage} alt='template' />
          ) : (
            <div className='flex h-full items-center justify-center'>
              <ClipLoader size={18} color='#7d9ecd' />
            </div>
          )}
        </ExpandModal>
      )}
      <div className='flex items-center justify-between'>
        <p className='text-lg font-bold'>Template List</p>
        {isAdmin && (
          <Link to='/template-management'>
            <Button variant='ghost'>
              <Settings />
              Settings
            </Button>
          </Link>
        )}
      </div>
      <div className='card-gradient flex h-38 flex-col gap-2 overflow-y-auto rounded-xl border p-2 pl-4'>
        <ul className='my-auto flex flex-col'>
          {templates.templates.map(template => (
            <li
              key={template}
              className='group hover:text-accent-foreground flex items-center gap-3 rounded-lg p-1'
            >
              <div className='bg-primary/80 h-1.5 w-1.5 shrink-0 rounded-full transition-all group-hover:scale-125' />
              {template}
              <div className='ml-auto flex items-center'>
                <Button
                  variant='ghost'
                  size='icon'
                  onClick={() => handleGetTemplateImage(template)}
                >
                  <Eye />
                </Button>
                <Button variant='ghost' size='icon'>
                  <Download />
                </Button>
              </div>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
};

export default TemplateList;
