import { useEffect, useState } from 'react';

import { ColumnDef } from '@tanstack/react-table';
import ClipLoader from 'react-spinners/ClipLoader';

import { useGetSourceData } from '@/apis/job';
import { Button } from '@/components/ui/button';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable';
import { Textarea } from '@/components/ui/textarea';
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
import { createSortableColumns } from '@/utils/dataframe';

const MainPage: React.FC = () => {
  const [inputCommand, setInputCommand] = useState<string>('');
  const [step, setStep] = useState<'source' | 'command'>('source');

  const { setSourceDataCommand, setSourceDataUrl, resetSource } =
    useSourceStore();

  const { addCommand, resetCommand } = useCommandStore();

  const {
    setColumns,
    setDataframe: setData,
    resetResult,
  } = useJobResultStore();

  const { resetJob, setCanSaveJob } = useJobStore();

  const { mutateAsync: sourceDataMutation, isPending: isSourceDataLoading } =
    useGetSourceData();

  const { connectStream, resetStream } = useStreamStore();

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

    setCanSaveJob(false);
    setInputCommand('');
  };

  useEffect(() => {
    connectStream();

    const cleanup = () => {
      resetResult();
      resetSource();
      resetCommand();
      resetJob();
      resetStream();
    };

    return () => {
      cleanup();
    };
  }, []);

  return (
    <div className='bg-gradient relative mx-auto flex h-screen w-full'>
      <ResizablePanelGroup direction='horizontal'>
        <ResizablePanel>
          <div className='mx-auto flex h-screen w-full max-w-[800px] grow-0 flex-col justify-between gap-4 p-8'>
            <div className='flex flex-1 flex-col gap-4 overflow-hidden'>
              <div className='flex gap-4'>
                <TemplateList />
                <SourceData />
              </div>

              <CommandList />
            </div>

            {/* Command Input */}
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
          <MainSideBar />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default MainPage;
