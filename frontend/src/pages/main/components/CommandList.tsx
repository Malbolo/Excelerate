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
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable';
import { ColumnDef } from '@tanstack/react-table';
import ClipLoader from 'react-spinners/ClipLoader';
import { toast } from 'sonner';

import { useSendCommandList } from '@/apis/job';
import { JobManagement } from '@/apis/jobManagement';
import { Button } from '@/components/ui/button';
import { createSortableColumns } from '@/lib/createSortableColumns';
import Command from '@/pages/main/components/Command';
import { useCommandStore } from '@/store/useCommandStore';
import { useJobResultStore } from '@/store/useJobResultStore';
import { useJobStore } from '@/store/useJobStore';
import { useSourceStore } from '@/store/useSourceStore';
import { useStreamStore } from '@/store/useStreamStore';
import { DataFrameRow } from '@/types/dataframe';

import SaveJobDialog from './SaveJobDialog';

const CommandList = ({ job }: { job?: JobManagement }) => {
  const { sourceDataUrl } = useSourceStore();

  const { commandList, reorderCommands, updateCommandStatus } =
    useCommandStore();

  const {
    setDataframe: setData,
    code,
    errorMsg,
    setCode,
    setColumns,
    setDownloadToken,
    setErrorMsg,
  } = useJobResultStore();

  const { isEditMode, setCanSaveJob } = useJobStore();
  const { streamId, resetLogs } = useStreamStore();

  const { mutateAsync: commandMutation, isPending: isCommandLoading } =
    useSendCommandList();

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;

    if (over && active.id !== over.id) {
      const oldIndex = parseInt(active.id.toString().split('-').pop() || '0');
      const newIndex = parseInt(over.id.toString().split('-').pop() || '0');

      reorderCommands(oldIndex, newIndex);
    }
    setCanSaveJob(false);
  };

  const handleSendCommandList = async () => {
    if (!streamId) {
      toast.error('Stream ID is not found');
      return;
    }

    resetLogs();

    const commands = commandList.map(({ content }) => content);
    const request = {
      command_list: commands,
      url: sourceDataUrl,
      stream_id: streamId,
    };

    if (!errorMsg) {
      Object.defineProperty(request, 'original_code', { value: code });
    }

    const response = await commandMutation(request);

    const columns: ColumnDef<DataFrameRow>[] = response.dataframe[0]
      ? createSortableColumns(response.dataframe[0])
      : [];

    setData(response.dataframe);
    setCode(response.codes[response.codes.length - 1]);
    setColumns(columns);
    setDownloadToken(response.download_token);
    setErrorMsg(response.error_msg || null);

    return response.error_msg;
  };

  const handleRun = async () => {
    setCanSaveJob(false);

    try {
      const errorMsg = await handleSendCommandList();

      commandList.forEach((_, idx) => {
        updateCommandStatus(idx, 'success');
      });

      if (errorMsg) {
        const errorIndex = errorMsg.command_index;
        updateCommandStatus(errorIndex, 'failed');
      } else {
        setCanSaveJob(true);
      }
    } catch (error) {
      commandList.forEach((_, idx) => {
        updateCommandStatus(idx, 'failed');
      });
    }
  };

  return (
    <section className='flex flex-1 flex-col gap-2 overflow-hidden'>
      <div className='flex items-center justify-between gap-2'>
        <p className='text-lg font-bold'>Command List</p>
        <div className='flex gap-2'>
          <Button
            disabled={
              commandList.length === 0 || isEditMode || isCommandLoading
            }
            onClick={handleRun}
          >
            {isCommandLoading ? (
              <ClipLoader size={18} color='#ffffff' />
            ) : (
              'Run'
            )}
          </Button>
          <SaveJobDialog job={job} />
        </div>
      </div>
      <div className='flex flex-1 flex-col gap-2 overflow-x-hidden overflow-y-auto'>
        <DndContext
          sensors={sensors}
          collisionDetection={closestCenter}
          onDragEnd={handleDragEnd}
        >
          <SortableContext
            items={commandList.map(
              (command, idx) => `${command.content}-${idx}`,
            )}
            strategy={verticalListSortingStrategy}
          >
            {commandList.map((command, index) => (
              <Command
                key={`${command.content}-${index}`}
                command={command}
                index={index}
              />
            ))}
          </SortableContext>
        </DndContext>
      </div>
    </section>
  );
};

export default CommandList;
