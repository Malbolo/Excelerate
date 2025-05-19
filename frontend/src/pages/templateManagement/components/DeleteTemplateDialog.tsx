import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface DeleteTemplateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  templateNameToDelete: string | null;
  onConfirmDelete: () => void;
  onCancelDelete: () => void;
}

const DeleteTemplateDialog = ({
  open,
  onOpenChange,
  templateNameToDelete,
  onConfirmDelete,
  onCancelDelete,
}: DeleteTemplateDialogProps) => {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className='font-bold'>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            <p>This action cannot be undone.</p>
            <p>This will permanently delete the template</p>
            <p className='py-1 font-bold text-black'>"{templateNameToDelete}"</p>
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={onCancelDelete}>Cancel</AlertDialogCancel>
          <AlertDialogAction onClick={onConfirmDelete} className='bg-red-600 hover:bg-red-700'>
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default DeleteTemplateDialog;
