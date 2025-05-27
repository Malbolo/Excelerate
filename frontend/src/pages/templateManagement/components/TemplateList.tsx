import { useState } from 'react';

import { Trash2 } from 'lucide-react';

import { useDeleteTemplate, useGetTemplates } from '@/apis/templates';
import { Button } from '@/components/ui/button';

import DeleteTemplateDialog from './DeleteTemplateDialog';

const TemplateList = () => {
  const { data: templatesResponse } = useGetTemplates();
  const { templates: templatesData = [] } = templatesResponse || {};
  const deleteTemplateMutate = useDeleteTemplate();

  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [templateNameToDelete, setTemplateNameToDelete] = useState<string | null>(null);

  const openDeleteDialog = (templateName: string) => {
    setTemplateNameToDelete(templateName);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (templateNameToDelete) {
      deleteTemplateMutate(templateNameToDelete);
    }
  };

  const handleCancelDelete = () => {
    setTemplateNameToDelete(null);
    setIsDeleteDialogOpen(false);
  };

  return (
    <div className='flex h-full flex-1 flex-col overflow-hidden'>
      <h2 className='mb-4 text-xl font-bold'>Template List</h2>
      {templatesData.length === 0 ? (
        <p className='text-center text-gray-500'>No templates found.</p>
      ) : (
        <ul className='flex-1 space-y-2 overflow-y-auto pr-2'>
          {templatesData.map(template => (
            <li key={template} className='card-gradient flex items-center justify-between rounded-lg border p-3'>
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
      )}
      <DeleteTemplateDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        templateNameToDelete={templateNameToDelete}
        onConfirmDelete={handleConfirmDelete}
        onCancelDelete={handleCancelDelete}
      />
    </div>
  );
};

export default TemplateList;
