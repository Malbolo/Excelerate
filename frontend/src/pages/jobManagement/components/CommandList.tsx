import { useState } from 'react';

import { Editor } from '@monaco-editor/react';
import { Command, TagIcon } from 'lucide-react';

import { useDeleteJob, useGetJobDetail } from '@/apis/jobManagement';
import {
  AlertDialog,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Button } from '@/components/ui/button';
import useInternalRouter from '@/hooks/useInternalRouter';

const CommandList = ({ selectedJobId }: { selectedJobId: string }) => {
  const deleteJobMutation = useDeleteJob();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const { data: selectedJob } = useGetJobDetail(selectedJobId);

  const { push } = useInternalRouter();

  const handleOpenDeleteDialog = () => {
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    deleteJobMutation(selectedJobId);
    setIsDeleteDialogOpen(false);
  };

  const handleJobEdit = () => {
    push(`/job-management/edit/${selectedJobId}`);
  };

  return (
    <>
      <div className='flex h-full w-full flex-col overflow-y-auto p-6'>
        <section className='space-y-4 divide-y'>
          <div className='pb-4'>
            <div className='flex items-center justify-between pb-2'>
              <h2 className='text-lg font-bold tracking-tight'>{selectedJob.title}</h2>
              <div className='flex shrink-0 items-center justify-center gap-2'>
                <Button variant='outline' onClick={handleJobEdit}>
                  Edit
                </Button>
                <Button variant='destructive' onClick={handleOpenDeleteDialog}>
                  Delete
                </Button>
              </div>
            </div>

            {selectedJob.description && <p className='mt-1.5 text-sm break-words'>{selectedJob.description}</p>}
          </div>

          <div className='space-y-6'>
            {(selectedJob.type || selectedJob.data_load_command) && (
              <div>
                <h3 className='text-accent-foreground mb-3 text-xs font-bold tracking-wider uppercase'>
                  Basic Information
                </h3>
                <div className='space-y-3 rounded-md border bg-white p-4 text-sm'>
                  {selectedJob.type && (
                    <div className='flex items-center'>
                      <span className='flex w-32 shrink-0 items-center gap-1 text-xs font-bold'>
                        <TagIcon className='mr-1.5 h-3.5 w-3.5 flex-shrink-0' />
                        Type
                      </span>
                      <span>{selectedJob.type}</span>
                    </div>
                  )}
                  {selectedJob.data_load_command && (
                    <div className='flex items-center'>
                      <span className='flex w-32 shrink-0 items-center gap-1 text-xs font-bold'>
                        <Command className='mr-1.5 h-3.5 w-3.5 flex-shrink-0' />
                        Data Load Cmd
                      </span>
                      <span className='break-all'>{selectedJob.data_load_command}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
            {selectedJob.commands && selectedJob.commands.length > 0 && (
              <div>
                <h3 className='text-accent-foreground mb-3 text-xs font-bold tracking-wider uppercase'>Command List</h3>
                <ol className='space-y-2'>
                  {selectedJob.commands.map(({ content, order }, index) => (
                    <li
                      className='flex items-center gap-2.5 rounded-md border bg-white p-3'
                      key={`${content}-${order}-${index}`}
                    >
                      <span className='w-5 text-right text-xs'>{order}.</span>
                      <p className='flex-1 text-sm'>{content}</p>
                    </li>
                  ))}
                </ol>
              </div>
            )}
            {selectedJob.code && (
              <div>
                <h3 className='text-accent-foreground mb-3 text-xs font-bold tracking-wider uppercase'>Source Code</h3>
                <div className='h-[400px] overflow-hidden rounded-md border'>
                  <Editor
                    height='100%'
                    defaultLanguage='python'
                    value={selectedJob.code}
                    options={{
                      readOnly: true,
                      domReadOnly: true,
                      minimap: { enabled: false },
                      scrollBeyondLastLine: false,
                      fontSize: 13,
                      renderWhitespace: 'boundary',
                      automaticLayout: true,
                    }}
                    theme='vs'
                  />
                </div>
              </div>
            )}
          </div>
        </section>
      </div>

      <AlertDialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
        <AlertDialogContent className='bg-white'>
          <AlertDialogHeader>
            <AlertDialogTitle className='font-bold'>Are you sure?</AlertDialogTitle>
            <AlertDialogDescription className='text-neutral-600'>
              <p>This will permanently delete the job "{selectedJob.title}".</p>
              <p>This action cannot be undone.</p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <Button variant='outline' onClick={() => setIsDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant='destructive' onClick={handleConfirmDelete}>
              Delete
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default CommandList;
