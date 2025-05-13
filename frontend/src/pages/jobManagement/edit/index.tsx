import { useEffect, useState } from 'react';

import { ColumnDef } from '@tanstack/react-table';
import { ArrowLeftIcon } from 'lucide-react';
import { useParams } from 'react-router-dom';
import ClipLoader from 'react-spinners/ClipLoader';
import { toast } from 'sonner';

import { useGetSourceData, useSendCommandList } from '@/apis/job';
import { useGetJobDetail } from '@/apis/jobManagement';
import { Button } from '@/components/ui/button';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable';
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
import { DataFrameRow } from '@/types/dataframe';

const JobEditPage = () => {
  const { jobId } = useParams();
  const getJobDetail = useGetJobDetail();

  const [inputCommand, setInputCommand] = useState<string>('');
  const [step, setStep] = useState<'source' | 'command'>('command');

  const { setSourceDataCommand, setSourceDataUrl, resetSource } =
    useSourceStore();

  const { addCommand, resetCommand, setCommandList } = useCommandStore();
  const { dataframe, setCode } = useJobResultStore();

  const {
    setColumns,
    setDataframe: setData,
    resetResult,
  } = useJobResultStore();

  const { resetJob, setCanSaveJob } = useJobStore();

  const { connectStream, resetStream } = useStreamStore();

  const { goBack } = useInternalRouter();

  const { mutateAsync: sourceDataMutation, isPending: isSourceDataLoading } =
    useGetSourceData();

  const { mutateAsync: commandMutation, isPending: isCommandLoading } =
    useSendCommandList();

  const fetchSourceData = async () => {
    const response = await sourceDataMutation(inputCommand);

    const columns: ColumnDef<DataFrameRow>[] = response.dataframe[0]
      ? createSortableColumns(response.dataframe[0])
      : [];

    setSourceDataCommand(inputCommand);
    setData(response.dataframe);
    setSourceDataUrl(response.url);
    setColumns(columns);
  };

  const handleSubmitCommand = async () => {
    if (!inputCommand.trim()) return;

    switch (step) {
      case 'source':
        await fetchSourceData();
        setStep('command');
        break;
      case 'command':
        const commands = inputCommand.split('\n\n');
        commands.forEach(command => {
          addCommand(command);
        });
        break;
    }

    setInputCommand('');
  };

  useEffect(() => {
    const initialize = async () => {
      if (!jobId) return;

      const data = await getJobDetail(jobId);
      const { data_load_command, data_load_url, commands, code } = data;

      setSourceDataCommand(data_load_command);
      setSourceDataUrl(data_load_url);
      setCode(code);
      setCommandList(
        commands.map(({ content, order }) => ({
          content,
          order,
          status: 'success',
        })),
      );

      setCanSaveJob(true);

      connectStream();

      // Stream ID가 설정될 때까지 대기
      await new Promise<void>(resolve => {
        const checkStreamId = setInterval(() => {
          if (useStreamStore.getState().streamId) {
            clearInterval(checkStreamId);
            resolve();
          }
        }, 100);
      });

      const command_list = commands.map(({ content }) => content);

      const currentStreamId = useStreamStore.getState().streamId;

      if (!currentStreamId) {
        toast.error('Stream ID is not found');
        return;
      }

      const response = await commandMutation({
        command_list,
        url: data_load_url,
        stream_id: currentStreamId,
      });

      setColumns(
        response.dataframe[0][0]
          ? createSortableColumns(response.dataframe[0][0])
          : [],
      );

      setData(response.dataframe[response.dataframe.length - 1]);
    };

    const cleanup = () => {
      resetResult();
      resetSource();
      resetCommand();
      resetJob();
      resetStream();
    };

    initialize();

    return () => {
      cleanup();
    };
  }, [jobId]);

  return (
    <div className='bg-gradient relative mx-auto flex h-screen w-full'>
      <ResizablePanelGroup direction='horizontal'>
        <ResizablePanel>
          <div className='mx-auto flex h-screen w-full max-w-[800px] grow-0 flex-col justify-between gap-4 p-8'>
            <div className='mb-4'>
              <Button
                variant='ghost'
                size='sm'
                onClick={goBack}
                className='flex items-center gap-2'
              >
                <ArrowLeftIcon className='h-4 w-4' />
                Back
              </Button>
            </div>

            <div className='flex flex-1 flex-col gap-4 overflow-hidden'>
              <div className='flex gap-4'>
                <TemplateList />
                <SourceData />
              </div>

              <CommandList />
            </div>

            <div className='flex gap-2'>
              <div className='relative flex-1'>
                <Textarea
                  value={inputCommand}
                  onChange={e => setInputCommand(e.target.value)}
                  onKeyDown={e => {
                    if (e.key === 'Enter' && !isSourceDataLoading) {
                      if (e.shiftKey) {
                        return;
                      }
                      e.preventDefault();
                      handleSubmitCommand();
                    }
                  }}
                  placeholder={
                    step === 'source'
                      ? 'Load the source data.'
                      : 'Please enter a command.'
                  }
                  disabled={isSourceDataLoading}
                  className='min-h-[42px] resize-none px-4 py-2.5 transition-all'
                />
                {isSourceDataLoading && (
                  <div className='absolute top-1/2 right-2 -translate-y-2/5'>
                    <ClipLoader size={18} color='#7d9ecd' />
                  </div>
                )}
              </div>

              <Button
                onClick={handleSubmitCommand}
                className='min-h-[42px] self-end'
                size='lg'
                disabled={isSourceDataLoading}
              >
                Enter
              </Button>
            </div>
          </div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        <ResizablePanel minSize={30} maxSize={60} defaultSize={30}>
          {!dataframe || isCommandLoading ? (
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
