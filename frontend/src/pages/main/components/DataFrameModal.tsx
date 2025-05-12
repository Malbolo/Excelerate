import DataTable from '@/components/DataTable';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { useJobResultStore } from '@/store/useJobResultStore';

interface DataFrameModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const DataFrameModal: React.FC<DataFrameModalProps> = ({ isOpen, onClose }) => {
  const { dataframe, columns } = useJobResultStore();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className='h-screen min-w-full'>
        <div className='my-4 h-full w-full overflow-auto rounded-lg border'>
          <DataTable columns={columns} data={dataframe!} />
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default DataFrameModal;
