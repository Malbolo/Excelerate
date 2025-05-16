import { useEffect, useState } from 'react';

import { ArrowLeftIcon } from 'lucide-react';
import { useParams } from 'react-router-dom';
import ClipLoader from 'react-spinners/ClipLoader';
import { toast } from 'sonner';

import { useSendCommandList } from '@/apis/job';
import { useGetJobDetail } from '@/apis/jobManagement';
import { Button } from '@/components/ui/button';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from '@/components/ui/resizable';
import { Textarea } from '@/components/ui/textarea';
import useInternalRouter from '@/hooks/useInternalRouter';
import { createSortableColumns } from '@/lib/createSortableColumns';
import CommandList from '@/pages/main/components/CommandList';
import MainSideBar from '@/pages/main/components/MainSideBar';
import SourceData from '@/pages/main/components/SourceData';
import TemplateList from '@/pages/main/components/TemplateList';
import { useCommandStore } from '@/store/useCommandStore';
import { useJobResultStore } from '@/store/useJobResultStore';
import { useJobStore } from '@/store/useJobStore';
import { useSourceStore } from '@/store/useSourceStore';
import { useStreamStore } from '@/store/useStreamStore';

const JobEditPage = () => {
  const { jobId } = useParams() as { jobId: string };
  const { goBack } = useInternalRouter();

  const [inputCommand, setInputCommand] = useState<string>('');
  const [step] = useState<'source' | 'command'>('command');

  const { data: jobDetail, isLoading: isJobDetailLoading } = useGetJobDetail(jobId);

  const { mutateAsync: commandMutation, isPending: isCommandLoading } = useSendCommandList();

  const { setSourceDataCommand, setSourceDataUrl, resetSource, setSourceParams } = useSourceStore();
  const { addCommand, resetCommand, setCommandList: setStoreCommandList } = useCommandStore();
  const { dataframe, setCode, setColumns, setDataframe: setData, resetResult } = useJobResultStore();
  const { resetJob, setCanSaveJob } = useJobStore();
  const { connectStream, resetStream } = useStreamStore();

  useEffect(() => {
    if (jobDetail) {
      const { data_load_command, data_load_url, commands, code, source_data } = jobDetail;

      setSourceDataCommand(data_load_command);
      setSourceDataUrl(data_load_url);
      setSourceParams(source_data);
      setCode(code);
      setStoreCommandList(
        commands.map(({ content, order }) => ({
          content,
          order,
          status: 'success',
        })),
      );
      setCanSaveJob(true);
    }
  }, [jobDetail, setSourceDataCommand, setSourceDataUrl, setCode, setStoreCommandList, setCanSaveJob]);

  const handleSubmitCommand = async () => {
    if (!inputCommand.trim()) return;

    const commands = inputCommand.split('\n\n');
    commands.forEach(command => {
      addCommand(command);
    });

    setInputCommand('');
  };

  useEffect(() => {
    if (!jobDetail) return;

    const initialize = async () => {
      connectStream();

      await new Promise<void>(resolve => {
        const checkStreamId = setInterval(() => {
          if (useStreamStore.getState().streamId) {
            clearInterval(checkStreamId);
            resolve();
          }
        }, 100);
      });

      const currentStreamId = useStreamStore.getState().streamId;
      if (!currentStreamId) {
        toast.error('Stream ID is not found');
        return;
      }

      if (jobDetail.commands && jobDetail.data_load_url) {
        const command_list = jobDetail.commands.map(({ content }) => content);
        try {
          const response = await commandMutation({
            command_list,
            url: jobDetail.data_load_url,
            stream_id: currentStreamId,
          });

          setColumns(response.dataframe[0] ? createSortableColumns(response.dataframe[0]) : []);
          setData(response.dataframe);
        } catch (error) {
          toast.error('Failed to execute initial commands.');
          console.error('Error during initial command execution:', error);
        }
      }
    };

    initialize();

    return () => {
      resetResult();
      resetSource();
      resetCommand();
      resetJob();
      resetStream();
    };
  }, [
    jobId,
    jobDetail,
    connectStream,
    commandMutation,
    setColumns,
    setData,
    resetResult,
    resetSource,
    resetCommand,
    resetJob,
    resetStream,
  ]);

  if (isJobDetailLoading) {
    return (
      <div className='flex h-screen w-full items-center justify-center'>
        <ClipLoader size={30} color='#7d9ecd' />
        <p className='ml-2'>Loading job details...</p>
      </div>
    );
  }

  return (
    <div className='bg-gradient relative mx-auto flex h-screen w-full'>
      <ResizablePanelGroup direction='horizontal'>
        <ResizablePanel>
          <div className='mx-auto flex h-screen w-full grow-0 flex-col justify-between gap-4 p-8'>
            <div>
              <Button variant='ghost' size='sm' onClick={goBack} className='flex items-center gap-2'>
                <ArrowLeftIcon className='h-4 w-4' />
                Back
              </Button>
            </div>

            <div className='@container flex flex-1 flex-col gap-4 overflow-hidden'>
              <div className='flex flex-col @md:flex-row'>
                <TemplateList />
                <SourceData />
              </div>
              <CommandList job={jobDetail} />
            </div>

            <div className='flex gap-2'>
              <div className='relative flex-1'>
                <Textarea
                  value={inputCommand}
                  onChange={e => setInputCommand(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter') {
                      if (e.shiftKey) {
                        return;
                      }
                      e.preventDefault();
                      handleSubmitCommand();
                    }
                  }}
                  placeholder={step === 'source' ? 'Load the source data.' : 'Please enter a command.'}
                  className='min-h-[42px] resize-none px-4 py-2.5 transition-all'
                />
              </div>

              <Button
                onClick={handleSubmitCommand}
                className='min-h-[42px] self-end'
                size='lg'
                disabled={isCommandLoading} // Added isCommandLoading here for safety
              >
                Enter
              </Button>
            </div>
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        <ResizablePanel minSize={30} maxSize={70} defaultSize={30}>
          {!dataframe || isCommandLoading ? ( // Added isSourceDataLoading for consistency
            <div className='flex h-full w-full items-center justify-center border-l bg-[#FAFCFF]'>
              <ClipLoader size={18} color='#7d9ecd' />
            </div>
          ) : (
            <MainSideBar />
          )}
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default JobEditPage;
