import { useEffect, useState } from 'react';

import { ColumnDef } from '@tanstack/react-table';
import ClipLoader from 'react-spinners/ClipLoader';

import { useGetSourceData, useSendCommandList } from '@/apis/job';
import { Button } from '@/components/ui/button';
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable';
import { Textarea } from '@/components/ui/textarea';
import CommandList from '@/pages/main/components/CommandList';
import MainSideBar from '@/pages/main/components/MainSideBar';
import SaveJobDialog from '@/pages/main/components/SaveJobDialog';
import SourceData from '@/pages/main/components/SourceData';
import TemplateList from '@/pages/main/components/TemplateList';
import { useJobStore } from '@/store/useJobStore';
import { DataFrame, DataFrameRow } from '@/types/dataframe';
import { TCommand } from '@/types/job';
import { createSortableColumns } from '@/utils/dataframe';

const MainPage: React.FC = () => {
  const [sourceData, setSourceData] = useState<string>('');
  const [sourceDataCommand, setSourceDataCommand] = useState<string>('');
  const [sourceDataUrl, setSourceDataUrl] = useState<string>('');
  const [commandList, setCommandList] = useState<TCommand[]>([]);
  const [command, setCommand] = useState<string>('');

  const [columns, setColumns] = useState<ColumnDef<DataFrameRow>[]>([]);
  const [data, setData] = useState<DataFrame | null>(null);
  const [code, setCode] = useState<string>('');
  const [logId, setLogId] = useState<string>('');
  const [downloadToken, setDownloadToken] = useState<string>('');

  const [step, setStep] = useState<'source' | 'command'>('source');
  const { isEditMode, setCanSaveJob } = useJobStore();

  const { mutateAsync: commandMutation, isPending: isCommandLoading } =
    useSendCommandList();
  const { mutateAsync: sourceDataMutation, isPending: isSourceDataLoading } =
    useGetSourceData();

  const fetchSourceData = async () => {
    const response = await sourceDataMutation(command);

    const columns: ColumnDef<DataFrameRow>[] = response.dataframe[0]
      ? createSortableColumns(response.dataframe[0])
      : [];

    setSourceDataCommand(command);
    setSourceData(command);
    setData(response.dataframe);
    setSourceDataUrl(response.url);
    setColumns(columns);
  };

  const handleSendCommandList = async () => {
    const commands = commandList.map(cmd => cmd.title);
    const response = await commandMutation({
      command_list: commands,
      url: sourceDataUrl,
    });

    const columns: ColumnDef<DataFrameRow>[] = response.dataframe[0][0]
      ? createSortableColumns(response.dataframe[0][0])
      : [];

    setData(response.dataframe[response.dataframe.length - 1]);
    setCode(response.codes[response.codes.length - 1]);
    setColumns(columns);
    setDownloadToken(response.download_token);
    setLogId(response.log_id);
  };

  const handleSubmitCommand = async () => {
    if (!command.trim()) return;

    switch (step) {
      case 'source':
        await fetchSourceData();
        setStep('command');
        break;
      case 'command':
        const commands = command.split('\n\n');
        setCommandList(prev => [
          ...prev,
          ...commands.map(command => ({
            title: command,
            status: 'pending' as const,
          })),
        ]);
        break;
    }

    setCommand('');
  };

  const handleRun = async () => {
    try {
      await handleSendCommandList();

      setCommandList(prevCommands =>
        prevCommands.map(command => ({
          ...command,
          status: 'success' as const,
        })),
      );

      setCanSaveJob(true);
    } catch (error) {
      setCommandList(prevCommands =>
        prevCommands.map(command => ({ ...command, status: 'fail' as const })),
      );
    }
  };

  useEffect(() => {
    return () => {
      setCanSaveJob(false);
    };
  }, [setCanSaveJob]);

  return (
    <div className='bg-gradient relative mx-auto flex h-screen w-full'>
      <ResizablePanelGroup direction='horizontal' className='h-full'>
        <ResizablePanel className='h-full'>
          <div className='mx-auto flex h-screen w-full max-w-[800px] flex-1 flex-col justify-between gap-4 overflow-auto p-8'>
            <div className='flex flex-1 flex-col gap-4'>
              <div className='flex gap-4'>
                <TemplateList />
                <SourceData sourceData={sourceData} />
              </div>

              <section className='flex flex-col gap-2 overflow-y-auto'>
                <div className='flex items-center justify-between gap-2'>
                  <p className='text-lg font-bold'>Command List</p>
                  <div className='flex gap-2'>
                    <Button
                      disabled={
                        commandList.length === 0 ||
                        isEditMode ||
                        isCommandLoading
                      }
                      onClick={handleRun}
                    >
                      {isCommandLoading ? (
                        <ClipLoader size={18} color='#ffffff' />
                      ) : (
                        'Run'
                      )}
                    </Button>
                    <SaveJobDialog
                      sourceData={sourceData}
                      sourceDataCommand={sourceDataCommand}
                      commandList={commandList}
                      code={code}
                    />
                  </div>
                </div>

                <CommandList
                  commandList={commandList}
                  setCommandList={setCommandList}
                />
              </section>
            </div>

            <div className='flex gap-2'>
              <div className='relative flex-1'>
                <Textarea
                  value={command}
                  onChange={e => setCommand(e.target.value)}
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
          <MainSideBar
            data={data}
            columns={columns}
            code={code}
            logId={logId}
            downloadToken={downloadToken}
          />
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default MainPage;
