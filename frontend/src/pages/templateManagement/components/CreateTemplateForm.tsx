import { ChangeEvent, useRef, useState } from 'react';

import { PlusCircle } from 'lucide-react';
import { toast } from 'sonner';

import { useCreateTemplate } from '@/apis/templates';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const CreateTemplateForm = () => {
  const createTemplateMutate = useCreateTemplate();
  const [newTemplateTitle, setNewTemplateTitle] = useState('');
  const [newTemplateFile, setNewTemplateFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setNewTemplateFile(event.target.files[0]);
    } else {
      setNewTemplateFile(null);
    }
  };

  const handleCustomFileButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleCreateTemplate = async () => {
    if (!newTemplateTitle.trim() || !newTemplateFile) {
      toast.error('Template name and file are required.');
      return;
    }
    createTemplateMutate({
      title: newTemplateTitle,
      file: newTemplateFile,
    });

    setNewTemplateTitle('');
    setNewTemplateFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = ''; // 파일 입력 초기화
    }
  };

  return (
    <div className='@container mb-6 flex flex-col border-b pb-6'>
      <div className='flex items-center justify-between'>
        <h2 className='mb-4 text-xl font-bold'>Add New Template</h2>
        <Button onClick={handleCreateTemplate} className='flex items-center gap-1.5'>
          <PlusCircle className='h-4 w-4' />
          Add Template
        </Button>
      </div>

      <div className='flex flex-col gap-6 @2xl:flex-row'>
        <div className='space-y-2'>
          <Label htmlFor='template-name' className='text-sm font-bold'>
            Template Name
          </Label>
          <Input
            id='template-name'
            value={newTemplateTitle}
            onChange={e => setNewTemplateTitle(e.target.value)}
            placeholder='e.g. Monthly Sales Report'
            className='w-full @2xl:w-96' // 반응형 너비 조정
          />
        </div>

        <div className='space-y-2'>
          <Label htmlFor='template-file' className='text-sm font-bold'>
            Template File
          </Label>
          <Input id='template-file' type='file' ref={fileInputRef} onChange={handleFileChange} className='hidden' />
          <div className='flex items-center gap-4'>
            {newTemplateFile ? (
              <span className='min-w-0 truncate text-sm text-gray-600' title={newTemplateFile.name}>
                {newTemplateFile.name}
              </span>
            ) : (
              <span className='text-sm text-gray-500'>No file selected</span>
            )}
            <Button
              type='button'
              variant='outline'
              onClick={handleCustomFileButtonClick}
              className='shrink-0 whitespace-nowrap'
            >
              {newTemplateFile ? 'Change File' : 'Choose File'}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateTemplateForm;
