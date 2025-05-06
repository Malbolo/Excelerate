import { useState } from 'react';

import { ColumnDef } from '@tanstack/react-table';

import { useGetSourceData, useSendCommandList } from '@/apis/job';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
  const [commandList, setCommandList] = useState<TCommand[]>([]);
  const [command, setCommand] = useState<string>('');

  const [columns, setColumns] = useState<ColumnDef<DataFrameRow>[]>([]);
  const [data, setData] = useState<DataFrame | null>(null);
  const [code, setCode] = useState<string>('');
  const [trace] = useState<string>('');

  const [step, setStep] = useState<'source' | 'command'>('source');
  const { isEditMode, setCanSaveJob } = useJobStore();

  const commandMutation = useSendCommandList();
  const sourceDataMutation = useGetSourceData();

  const fetchSourceData = async () => {
    const response = await sourceDataMutation(command);

    const columns: ColumnDef<DataFrameRow>[] = response.dataframe[0]
      ? createSortableColumns(response.dataframe[0])
      : [];

    setSourceDataCommand(command);
    setData(response.dataframe);
    setSourceData(response.url);
    setColumns(columns);
  };

  const handleSendCommandList = async () => {
    const commands = commandList.map(cmd => cmd.title);
    const response = await commandMutation({
      command_list: commands,
      url: sourceData,
    });

    const columns: ColumnDef<DataFrameRow>[] = response.dataframe[0][0]
      ? createSortableColumns(response.dataframe[0][0])
      : [];

    setData(response.dataframe[response.dataframe.length - 1]);
    setCode(response.codes[response.codes.length - 1]);
    setColumns(columns);
  };

  const handleSubmitCommand = async () => {
    if (!command.trim()) return;

    switch (step) {
      case 'source':
        await fetchSourceData();
        setStep('command');
        break;
      case 'command':
        setCommandList(prev => [
          ...prev,
          { title: command, status: 'pending' },
        ]);
        break;
    }

    setCommand('');
  };

  const handleRun = async () => {
    const updateCommandStatus = (
      index: number,
      status: 'processing' | 'success',
    ) => {
      setCommandList(prevCommands =>
        prevCommands.map((command, idx) =>
          idx === index ? { ...command, status } : command,
        ),
      );
    };

    /**
     * 추후 소켓 통신 시 제거 예정
     */
    for (let i = 0; i < commandList.length; i++) {
      updateCommandStatus(i, 'processing');
      await new Promise(resolve => setTimeout(resolve, 1000));
      updateCommandStatus(i, 'success');
    }

    handleSendCommandList();
    // TODO: 모든 command가 성공 시 저장 가능 상태로 변경
    setCanSaveJob(true);
  };

  return (
    <div className='relative mx-auto flex h-full w-full overflow-hidden'>
      <div className='mx-auto flex w-full max-w-[800px] flex-1 flex-col justify-between gap-4 p-8'>
        <div className='flex flex-col gap-4'>
          <div className='flex gap-4'>
            <TemplateList />
            <SourceData sourceData={sourceData} />
          </div>

          <section className='flex flex-col gap-2'>
            <div className='flex items-center justify-between gap-2'>
              <p className='text-lg font-bold'>Command List</p>
              <div className='flex gap-2'>
                <Button
                  variant={
                    commandList.length !== 0 && !isEditMode
                      ? 'default'
                      : 'disabled'
                  }
                  onClick={handleRun}
                >
                  Run
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
          <Input
            value={command}
            onChange={e => setCommand(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmitCommand()}
            placeholder={
              step === 'source'
                ? 'Load the source data.'
                : 'Please enter a command.'
            }
          />

          <Button onClick={handleSubmitCommand} className='cursor-pointer'>
            Enter
          </Button>
        </div>
      </div>

      <MainSideBar data={data} columns={columns} code={code} trace={trace} />
    </div>
  );
};

export default MainPage;
