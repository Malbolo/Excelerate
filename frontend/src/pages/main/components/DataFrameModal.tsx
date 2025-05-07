import { ColumnDef } from '@tanstack/react-table';

import DataTable from '@/components/DataTable';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { DataFrame, DataFrameRow } from '@/types/dataframe';

interface DataFrameModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: DataFrame;
  columns: ColumnDef<DataFrameRow>[];
}

const DataFrameModal: React.FC<DataFrameModalProps> = ({
  isOpen,
  onClose,
  data,
  columns,
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className='h-screen min-w-full'>
        <div className='h-full w-full overflow-auto pt-5'>
          <DataTable columns={columns} data={data} />
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default DataFrameModal;
