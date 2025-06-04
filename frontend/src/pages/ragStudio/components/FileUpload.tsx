import { useCallback, useState } from 'react';

import { Upload } from 'lucide-react';
import { useDropzone } from 'react-dropzone';

import { useInsertRagDocument } from '@/apis/ragStudio';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';

export const FileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const insertRagDocumentMutate = useInsertRagDocument();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    setUploadProgress(0);

    // 파일 업로드 시뮬레이션
    for (let i = 0; i < acceptedFiles.length; i++) {
      const file = acceptedFiles[i];

      // 진행률 업데이트
      setUploadProgress(((i + 1) / acceptedFiles.length) * 100);

      insertRagDocumentMutate(file);
    }

    setUploading(false);
    setUploadProgress(0);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    multiple: true,
  });

  return (
    <div className='space-y-6'>
      {/* 드래그 앤 드롭 영역 */}
      <Card>
        <CardContent className='p-6'>
          <div
            {...getRootProps()}
            className={cn(
              'cursor-pointer rounded-lg border border-dashed p-8 text-center transition-colors',
              isDragActive ? 'border-primary bg-primary/5' : 'border-muted-foreground/25',
              uploading && 'pointer-events-none opacity-50',
            )}
          >
            <input {...getInputProps()} />
            <Upload className='mx-auto mb-4 h-4 w-4' />
            <div>
              <p className='mb-2 text-xs'>Drag and drop files here or click to upload</p>
              <p className='text-muted-foreground text-xs'>Supports PDF, TXT, and DOCX files (up to 10MB)</p>
            </div>
          </div>

          {uploading && (
            <div className='mt-4'>
              <div className='mb-2 flex items-center justify-between'>
                <span className='text-sm font-medium'>uploading...</span>
                <span className='text-muted-foreground text-sm'>{uploadProgress.toFixed(0)}%</span>
              </div>
              <Progress value={uploadProgress} className='w-full' />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
