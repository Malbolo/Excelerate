import { useState } from 'react';

import {
  DndContext,
  DragEndEvent,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  useSensor,
  useSensors,
} from '@dnd-kit/core';
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import Editor from '@monaco-editor/react';
import { ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown, DownloadIcon } from 'lucide-react';
import { toast } from 'sonner';

import { useSendCommandList } from '@/apis/job';
import { MPythonCode } from '@/mocks/datas/pythonCode';
import { DataFrame, DataFrameRow } from '@/types/dataframe';

import Command from '../components/Command';
import DataTable from '../components/DataTable';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { cn } from '../lib/utils';
import { TCommand } from '../types/job';

const MainPage: React.FC = () => {
  const [step, setStep] = useState<'source' | 'command'>('source');

  const [commandList, setCommandList] = useState<TCommand[]>([]);
  const [command, setCommand] = useState<string>('');
  const [sourceData, setSourceData] = useState<string>('');

  const [columns, setColumns] = useState<ColumnDef<DataFrameRow>[]>([]);
  const [data, setData] = useState<DataFrame | null>(null);
  const [code, setCode] = useState<string>('');

  const [view, setView] = useState<'data' | 'code' | 'trace'>('data');
  const [isEditMode, setIsEditMode] = useState<boolean>(false);

  const commandMutation = useSendCommandList();

  const handleSendCommandList = () => {
    const commands = commandList.map(cmd => cmd.title);

    commandMutation(commands, {
      onSuccess: response => {
        setData(response.dataframe);
        setCode(response.code);

        // response.dataframe을 기반으로 컬럼 생성
        if (response.dataframe && response.dataframe.length > 0) {
          const columns: ColumnDef<DataFrameRow>[] = Object.keys(
            response.dataframe[0],
          ).map(key => ({
            accessorKey: key,
            header: ({ column }) => (
              <Button
                variant='ghost'
                onClick={() =>
                  column.toggleSorting(column.getIsSorted() === 'asc')
                }
                className='cursor-pointer'
              >
                {key}
                <ArrowUpDown className='ml-2 h-4 w-4' />
              </Button>
            ),
          }));
          setColumns(columns);
        }

        toast.success('Commands processed successfully');
      },
    });
  };

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const fetchSourceData = async () => {
    if (command.trim() !== '베트남 지사 A 제품 데이터 가져와')
      throw new Error('Invalid command');
    const data = '베트남 지사 A 제품';
    setSourceData(data);
  };

  const handleLoad = async () => {
    if (!command) return;
    if (!command.trim()) return;

    try {
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
    } catch (err) {
      alert('Invalid command');
    }

    setCommand('');
  };

  const handleEditCommand = (command: string, newCommand: string) => {
    setCommandList(prev =>
      prev.map(cmd =>
        cmd.title === command
          ? { status: 'pending', title: newCommand }
          : { status: 'pending', title: cmd.title },
      ),
    );
  };

  const handleDeleteCommand = (command: string) => {
    setCommandList(prev =>
      prev
        .filter(prevCommand => prevCommand.title !== command)
        .map(cmd => ({ ...cmd, status: 'pending' })),
    );
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

    for (let i = 0; i < commandList.length; i++) {
      updateCommandStatus(i, 'processing');
      await new Promise(resolve => setTimeout(resolve, 1000));
      updateCommandStatus(i, 'success');
    }

    handleSendCommandList();
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      setCommandList(items => {
        const oldIndex = items.findIndex(item => item.title === active.id);
        const newIndex = items.findIndex(item => item.title === over.id);

        return arrayMove(items, oldIndex, newIndex).map(item => ({
          ...item,
          status: 'pending',
        }));
      });
    }
  };

  return (
    <div className='relative mx-auto flex h-full w-full overflow-hidden'>
      <div className='mx-auto flex w-full max-w-[800px] flex-1 flex-col justify-between gap-4 p-8'>
        <div className='flex flex-col gap-4'>
          <div className='flex gap-4'>
            <section className='flex max-h-48 flex-1 flex-col gap-2'>
              <p className='text-lg font-bold'>Template List</p>
              <div className='flex grow flex-col gap-4 overflow-y-auto border border-black p-2'>
                <ul className='list-inside list-disc'>
                  <li>Template 1</li>
                  <li>Template 2</li>
                  <li>Template 3</li>
                  <li>Template 4</li>
                  <li>Template 5</li>
                  <li>Template 6</li>
                  <li>Template 7</li>
                  <li>Template 8</li>
                  <li>Template 9</li>
                  <li>Template 10</li>
                </ul>
              </div>
            </section>

            <section className='flex max-h-48 flex-1 flex-col gap-2'>
              <p className='text-lg font-bold'>Source Data</p>
              <div className='flex grow flex-col justify-center border border-black p-2 text-center'>
                {sourceData ? (
                  <p>{sourceData}</p>
                ) : (
                  <>
                    <p>Source data hasn't been loaded.</p>
                    <p>Please load it using a command.</p>
                  </>
                )}
              </div>
            </section>
          </div>

          <section className='flex flex-col gap-2'>
            <div className='flex items-center justify-between gap-2'>
              <p className='text-lg font-bold'>Command List</p>
              {commandList.length === 0 ? (
                <Button variant='disabled'>run</Button>
              ) : (
                <Button onClick={handleRun} className='cursor-pointer'>
                  run
                </Button>
              )}
            </div>
            <div className='flex flex-col gap-2'>
              <DndContext
                sensors={sensors}
                collisionDetection={closestCenter}
                onDragEnd={handleDragEnd}
              >
                <SortableContext
                  items={commandList.map(cmd => cmd.title)}
                  strategy={verticalListSortingStrategy}
                >
                  {commandList.map(command => (
                    <Command
                      key={command.title}
                      id={command.title}
                      command={command.title}
                      status={command.status}
                      onDelete={() => handleDeleteCommand(command.title)}
                      onEdit={handleEditCommand}
                      isEditMode={isEditMode}
                      setIsEditMode={setIsEditMode}
                    />
                  ))}
                </SortableContext>
              </DndContext>
            </div>
          </section>
        </div>

        <div className='flex gap-2'>
          <Input
            value={command}
            onChange={e => setCommand(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleLoad()}
            placeholder='Load the source data.'
          />

          <Button onClick={handleLoad} className='cursor-pointer'>
            Enter
          </Button>
        </div>
      </div>

      <div className='h-full w-[400px]'>
        <div className='border-border relative flex h-full w-full flex-col border-l bg-[#F0F0F0] px-2 py-6'>
          <div className='flex translate-y-[1px] self-end'>
            <div
              onClick={() => setView('data')}
              className={cn(
                'cursor-pointer rounded-t-md border px-2',
                view === 'data'
                  ? 'border-[#034EA2] bg-[#034EA2] text-white'
                  : 'border-border bg-white',
              )}
            >
              Data
            </div>
            <div
              onClick={() => setView('code')}
              className={cn(
                'cursor-pointer rounded-t-md border px-2',
                view === 'code'
                  ? 'border-[#034EA2] bg-[#034EA2] text-white'
                  : 'border-border bg-white',
              )}
            >
              Code
            </div>
            <div
              onClick={() => setView('trace')}
              className={cn(
                'cursor-pointer rounded-t-md border px-2',
                view === 'trace'
                  ? 'border-[#034EA2] bg-[#034EA2] text-white'
                  : 'border-border bg-white',
              )}
            >
              Trace
            </div>
          </div>

          {view === 'data' ? (
            <div className='flex h-[90vh] flex-col'>
              {data ? (
                <>
                  <DataTable columns={columns} data={data} />
                  <div className='absolute right-2 bottom-2 z-10 cursor-pointer rounded-full bg-black p-3'>
                    <DownloadIcon color='white' size={18} />
                  </div>
                </>
              ) : (
                <div className='border-border flex h-full items-center justify-center rounded-tl-md rounded-b-md border bg-white p-2'>
                  No data
                </div>
              )}
            </div>
          ) : view === 'code' ? (
            <div className='border-border grow rounded-tl-md rounded-b-md border bg-white py-2'>
              {code ? (
                <Editor
                  defaultLanguage='python'
                  defaultValue={MPythonCode}
                  options={{
                    readOnly: true,
                    domReadOnly: true,
                    minimap: { enabled: false },
                  }}
                />
              ) : (
                <div className='flex h-full items-center justify-center'>
                  No code
                </div>
              )}
            </div>
          ) : (
            <div className='border-border grow rounded-tl-md rounded-b-md border bg-white'>
              Trace
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MainPage;
