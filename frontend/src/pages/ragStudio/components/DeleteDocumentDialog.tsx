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

interface DeleteDocumentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  documentNameToDelete: string | null;
  onConfirmDelete: () => void;
  onCancelDelete: () => void;
}

const DeleteDocumentDialog = ({
  open,
  onOpenChange,
  documentNameToDelete,
  onConfirmDelete,
  onCancelDelete,
}: DeleteDocumentDialogProps) => {
  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle className='font-bold'>Are you sure?</AlertDialogTitle>
          <AlertDialogDescription>
            <p>This action cannot be undone.</p>
            <p>This will permanently delete the document</p>
            <p className='py-1 font-bold text-black'>"{documentNameToDelete}"</p>
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

export default DeleteDocumentDialog;
