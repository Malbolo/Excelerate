import { useState } from 'react';

import { Trash2 } from 'lucide-react';

import { useDeleteRagDocument, useGetRagDocuments } from '@/apis/ragStudio';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

import DeleteDocumentDialog from './DeleteDocumentDialog';

const DocumentManagement = () => {
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState<boolean>(false);
  const [documentNameToDelete, setDocumentNameToDelete] = useState<string | null>(null);
  const [documentIdToDelete, setDocumentIdToDelete] = useState<string | null>(null);

  const { data: documents } = useGetRagDocuments();
  const deleteRagDocumentmutate = useDeleteRagDocument();

  const openDeleteDialog = (docId: string, docName: string) => {
    setDocumentIdToDelete(docId);
    setDocumentNameToDelete(docName);
    setIsDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async () => {
    if (documentIdToDelete) {
      deleteRagDocumentmutate(documentIdToDelete);
    }
  };

  const handleCancelDelete = () => {
    setDocumentNameToDelete(null);
    setIsDeleteDialogOpen(false);
  };

  return (
    <div className='h-full overflow-hidden'>
      <Card className='h-full overflow-y-auto'>
        <CardContent className='h-full'>
          <ul className='h-full'>
            {documents.map(document => (
              <li
                className='group hover:text-accent-foreground flex items-center gap-3 rounded-lg p-1'
                key={document.doc_id}
              >
                <div className='bg-primary/80 h-1.5 w-1.5 shrink-0 rounded-full transition-all group-hover:scale-125' />
                {document.file_name}
                <Button
                  variant='ghost'
                  size='icon'
                  onClick={() => openDeleteDialog(document.doc_id, document.file_name)}
                  className='ml-auto text-red-500 hover:bg-red-100 hover:text-red-700'
                  aria-label={`Delete template ${document.file_name}`}
                >
                  <Trash2 className='h-4 w-4' />
                </Button>
              </li>
            ))}
          </ul>
          <DeleteDocumentDialog
            open={isDeleteDialogOpen}
            onOpenChange={setIsDeleteDialogOpen}
            documentNameToDelete={documentNameToDelete}
            onConfirmDelete={handleConfirmDelete}
            onCancelDelete={handleCancelDelete}
          />
        </CardContent>
      </Card>
    </div>
  );
};

export default DocumentManagement;
