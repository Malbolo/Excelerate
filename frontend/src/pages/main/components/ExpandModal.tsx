import { Dialog, DialogContent } from '@/components/ui/dialog';

interface DataFrameModalProps {
  children: React.ReactNode;
  isOpen: boolean;
  onClose: () => void;
}

const ExpandModal: React.FC<DataFrameModalProps> = ({
  children,
  isOpen,
  onClose,
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className='h-screen min-w-full'>
        <div className='my-4 h-full w-full overflow-auto rounded-lg border'>
          {children}
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default ExpandModal;
