import { useRef, useState } from 'react';

import { ArrowLeftIcon, PlusCircle, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

import { useCreateTemplate, useDeleteTemplate, useGetTemplates } from '@/apis/templates';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import useInternalRouter from '@/hooks/useInternalRouter';

const TemplateManagementPage = () => {
  const { data: templatesResponse } = useGetTemplates();
  const { templates: templatesData } = templatesResponse;
  const { goBack } = useInternalRouter();

  const createTemplateMutate = useCreateTemplate();
  const deleteTemplateMutate = useDeleteTemplate();

  const [newTemplateTitle, setNewTemplateTitle] = useState('');
  const [newTemplateFile, setNewTemplateFile] = useState<File | null>(null);

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [templateNameToDelete, setTemplateNameToDelete] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
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
      fileInputRef.current.value = '';
    }
  };

  const openDeleteDialog = (templateName: string) => {
    setTemplateNameToDelete(templateName);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (templateNameToDelete) {
      deleteTemplateMutate(templateNameToDelete);
      setTemplateNameToDelete(null);
      setIsDeleteDialogOpen(false);
      toast.success(`Template "${templateNameToDelete}" deleted successfully.`);
    }
  };

  return (
    <section className='flex flex-1 flex-col gap-6 bg-white p-6'>
      <div className='mb-6 flex items-center gap-4'>
        <Button variant='ghost' size='sm' onClick={goBack} className='flex items-center gap-2'>
          <ArrowLeftIcon className='h-4 w-4' />
          Back
        </Button>
      </div>
      <div className='mb-6 border-b border-gray-200 pb-6'>
        <h2 className='mb-4 text-xl font-semibold text-gray-700'>Add New Template</h2>
        <div className='flex flex-col gap-y-6 md:flex-row md:items-end md:gap-x-4'>
          <div className='space-y-2'>
            <Label htmlFor='template-name'>Template Name</Label>
            <Input
              id='template-name'
              value={newTemplateTitle}
              onChange={e => setNewTemplateTitle(e.target.value)}
              placeholder='e.g., Monthly Sales Report'
              className='w-full'
            />
          </div>

          <div className='space-y-2'>
            <Label htmlFor='template-file'>Template File</Label>
            <Input id='template-file' type='file' ref={fileInputRef} onChange={handleFileChange} className='hidden' />
            <div className='flex items-center gap-3'>
              <Button
                type='button'
                variant='outline'
                onClick={handleCustomFileButtonClick}
                className='shrink-0 whitespace-nowrap'
              >
                {newTemplateFile ? 'Change File' : 'Choose File'}
              </Button>
              {newTemplateFile ? (
                <span className='min-w-0 truncate text-sm text-gray-600' title={newTemplateFile.name}>
                  {newTemplateFile.name}
                </span>
              ) : (
                <span className='text-sm text-gray-500'>No file selected</span>
              )}
            </div>
          </div>

          <Button onClick={handleCreateTemplate} className='mt-2 w-full shrink-0 md:mt-0 md:w-auto'>
            <PlusCircle className='mr-2 h-4 w-4' />
            Add Template
          </Button>
        </div>
      </div>

      <div>
        <h2 className='mb-4 text-xl font-semibold text-gray-700'>Template List</h2>

        <ul className='space-y-2'>
          {templatesData.map(template => (
            <li
              key={template}
              className='flex items-center justify-between rounded-md border border-gray-200 bg-white p-3'
            >
              <span className='text-sm font-medium text-gray-800'>{template}</span>
              <Button
                variant='ghost'
                size='icon'
                onClick={() => openDeleteDialog(template)}
                className='text-red-500 hover:bg-red-100 hover:text-red-700'
                aria-label={`Delete template ${template}`}
              >
                <Trash2 className='h-4 w-4' />
              </Button>
            </li>
          ))}
        </ul>
      </div>

      {/* 삭제 대화 모달 */}
      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription>
              This action cannot be undone. This will permanently delete the template "
              <strong>{templateNameToDelete}</strong>".
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setTemplateNameToDelete(null)}>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmDelete} className='bg-red-600 hover:bg-red-700'>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </section>
  );
};
export default TemplateManagementPage;
