import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Job } from '@/types/scheduler';

interface CreateScheduleModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  selectedJobs: Job[];
}

const CreateScheduleModal = ({
  isOpen,
  onOpenChange,
  selectedJobs,
}: CreateScheduleModalProps) => {
  const handleSubmit = () => {
    onOpenChange(false);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>스케줄 생성 확인</DialogTitle>
          <DialogDescription>
            선택된 {selectedJobs.length}개의 JOB으로 스케줄을 생성합니다.
          </DialogDescription>
        </DialogHeader>
        <div className='max-h-60 overflow-y-auto py-4'>
          <h4 className='mb-2 font-medium'>선택된 JOB:</h4>
          <ul className='list-inside list-decimal space-y-1 text-sm'>
            {selectedJobs.map(job => (
              <li key={job.jobId}>{job.title}</li>
            ))}
          </ul>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant='outline'>취소</Button>
          </DialogClose>
          <Button type='button' onClick={handleSubmit}>
            생성하기
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CreateScheduleModal;
