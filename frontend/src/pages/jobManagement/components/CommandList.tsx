import { useState } from 'react';

import { Editor } from '@monaco-editor/react';
import { useSearchParams } from 'react-router-dom';

import { JobResponse, useDeleteJob } from '@/apis/jobManagement';
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
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';

const CommandList = ({ selectedJob }: { selectedJob: JobResponse | null }) => {
  const [searchParams] = useSearchParams();
  const page = searchParams.get('page') || '1';
  const keyword = searchParams.get('keyword') || '';

  const deleteJobMutation = useDeleteJob();
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const handleOpenDeleteDialog = () => {
    if (!selectedJob) return;
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = () => {
    if (!selectedJob) return;
    deleteJobMutation({ id: selectedJob.id, page, keyword });
    setIsDeleteDialogOpen(false);
  };

  const handleJobEdit = () => {
    if (!selectedJob) return;
    console.log('Edit job:', selectedJob.id);
  };

  if (!selectedJob) {
    return (
      <div className='flex h-full w-[40%] flex-col items-center justify-center border-l border-neutral-200 bg-white p-8'>
        <p className='text-lg text-neutral-500'>Please select a job.</p>
      </div>
    );
  }

  return (
    <>
      <div className='flex h-full w-[40%] flex-col overflow-hidden border-l border-neutral-200 bg-white'>
        <ScrollArea className='h-full flex-grow'>
          <div className='p-6'>
            <section className='space-y-6'>
              <div>
                <h2 className='text-2xl font-semibold tracking-tight text-neutral-900'>
                  {selectedJob.title}
                </h2>
                {selectedJob.description && (
                  <p className='mt-1.5 text-sm text-neutral-600'>
                    {selectedJob.description}
                  </p>
                )}
              </div>

              <Separator className='bg-neutral-200' />

              <div className='space-y-6'>
                {(selectedJob.type || selectedJob.data_load_command) && (
                  <div>
                    <h3 className='mb-3 text-xs font-semibold tracking-wider text-neutral-500 uppercase'>
                      Basic Information
                    </h3>
                    <div className='space-y-3 rounded-md border border-neutral-200 bg-neutral-50 p-4 text-sm'>
                      {selectedJob.type && (
                        <div className='flex'>
                          <span className='w-32 shrink-0 text-neutral-500'>
                            Type
                          </span>
                          <span className='text-neutral-700'>
                            {selectedJob.type}
                          </span>
                        </div>
                      )}
                      {selectedJob.data_load_command && (
                        <div className='flex'>
                          <span className='w-32 shrink-0 text-neutral-500'>
                            Data Load Cmd
                          </span>
                          <span className='break-all text-neutral-700'>
                            {selectedJob.data_load_command}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                {selectedJob.commands && selectedJob.commands.length > 0 && (
                  <div>
                    <h3 className='mb-3 text-xs font-semibold tracking-wider text-neutral-500 uppercase'>
                      Command List
                    </h3>
                    <ol className='space-y-2'>
                      {selectedJob.commands.map(({ content, order }, index) => (
                        <li
                          className='flex items-start gap-2.5 rounded-md border border-neutral-200 bg-white p-3 transition-colors hover:bg-neutral-50'
                          key={`${content}-${order}-${index}`}
                        >
                          <span className='w-5 pt-px text-right text-xs text-neutral-400'>
                            {order}.
                          </span>
                          <p className='flex-1 text-sm text-neutral-700'>
                            {content}
                          </p>
                        </li>
                      ))}
                    </ol>
                  </div>
                )}
                {selectedJob.code && (
                  <div>
                    <h3 className='mb-3 text-xs font-semibold tracking-wider text-neutral-500 uppercase'>
                      Source Code
                    </h3>
                    <div className='h-[300px] overflow-hidden rounded-md border border-neutral-200'>
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
          <div className='flex shrink-0 items-center justify-center gap-3 border-t border-neutral-200 p-4'>
            <Button
              variant='destructive'
              className='h-10 w-full sm:w-auto sm:flex-grow'
              onClick={handleOpenDeleteDialog}
            >
              Delete
            </Button>
            <Button
              variant='outline'
              className='h-10 w-full border-neutral-300 text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900 sm:w-auto sm:flex-grow'
              onClick={handleJobEdit}
            >
              Edit
            </Button>
          </div>
        </ScrollArea>
      </div>

      <AlertDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
      >
        <AlertDialogContent className='bg-white'>
          <AlertDialogHeader>
            <AlertDialogTitle className='text-neutral-900'>
              Are you sure?
            </AlertDialogTitle>
            <AlertDialogDescription className='text-neutral-600'>
              This will permanently delete the job "{selectedJob.title}". This
              action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel
              className='border-neutral-300 text-neutral-700 hover:bg-neutral-100 hover:text-neutral-900'
              onClick={() => setIsDeleteDialogOpen(false)}
            >
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction
              className='bg-neutral-900 text-neutral-50 hover:bg-neutral-700'
              onClick={handleConfirmDelete}
            >
              Confirm Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
};

export default CommandList;
