import { zodResolver } from '@hookform/resolvers/zod';
import { format as formatDate } from 'date-fns';
import { ko } from 'date-fns/locale';
import { CalendarIcon } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { Job } from '@/types/scheduler';

const formSchema = z
  .object({
    batchTitle: z.string().min(1, '스케줄 제목을 입력해주세요.'),
    batchDescription: z.string().min(1, '설명을 입력해주세요.'),
    successEmail: z
      .string()
      .min(1, '성공 알림 이메일을 입력해주세요.')
      .email({ message: '유효한 이메일 주소를 입력해주세요.' }),
    failEmail: z
      .string()
      .min(1, '실패 알림 이메일을 입력해주세요.')
      .email({ message: '유효한 이메일 주소를 입력해주세요.' }),
    interval: z.enum(['daily', 'weekly', 'monthly'], {
      required_error: '실행 주기를 선택해주세요.',
    }),
    startDate: z.date({
      required_error: '시작일을 선택해주세요.',
    }),
    endDate: z.date({
      required_error: '종료일을 선택해주세요.',
    }),
    executionTime: z.string().regex(/^([01]\d|2[0-3]):([0-5]\d)$/, {
      message: '시간을 HH:MM 형식으로 입력해주세요. (예: 09:00, 14:30)',
    }),
  })
  .refine(
    data => {
      if (data.startDate && data.endDate) {
        const start = new Date(data.startDate.setHours(0, 0, 0, 0));
        const end = new Date(data.endDate.setHours(0, 0, 0, 0));
        return end >= start;
      }
      return true;
    },
    {
      message: '종료일은 시작일보다 같거나 이후여야 합니다.',
      path: ['endDate'],
    },
  );

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
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      batchTitle: '',
      batchDescription: '',
      successEmail: '',
      failEmail: '',
      interval: undefined,
      startDate: undefined,
      endDate: undefined,
      executionTime: '09:00',
    },
  });

  async function onSubmit(values: z.infer<typeof formSchema>) {
    console.log('Form Data Submitted:', values);
    console.log('Selected Jobs Submitted:', selectedJobs);
    await new Promise(resolve => setTimeout(resolve, 1000));
    onOpenChange(false);
    form.reset();
  }

  const handleOpenChange = (open: boolean) => {
    onOpenChange(open);
    if (!open) {
      form.reset();
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className='flex max-h-[85vh] flex-col sm:max-w-3xl'>
        <DialogHeader>
          <DialogTitle>새 스케줄 생성</DialogTitle>
          <DialogDescription>
            선택된 {selectedJobs.length}개의 JOB으로 새 스케줄을 설정합니다.
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className='flex-grow pr-6'>
          <div className='mb-4 rounded-md border bg-gray-50 p-3'>
            <h4 className='mb-2 text-sm font-medium text-gray-700'>
              선택된 JOB ({selectedJobs.length}):
            </h4>
            <ul className='max-h-24 list-inside list-decimal space-y-1 overflow-y-auto text-xs text-gray-600'>
              {selectedJobs.map(job => (
                <li key={job.jobId}>{job.title}</li>
              ))}
            </ul>
          </div>

          <Separator className='my-4' />

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-4'>
              <div className='grid grid-cols-1 gap-x-8 gap-y-6 md:grid-cols-2'>
                <div className='space-y-6'>
                  <FormField
                    control={form.control}
                    name='batchTitle'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          스케줄 제목
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder='예: 일일 판매 데이터 집계'
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name='batchDescription'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          설명 <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder='스케줄에 대한 설명을 입력하세요.'
                            className='resize-none'
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <Separator className='my-4 md:hidden' />
                  <FormField
                    control={form.control}
                    name='successEmail'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          성공 알림 이메일
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type='email'
                            placeholder='성공 시 알림받을 이메일'
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name='failEmail'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          실패 알림 이메일
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type='email'
                            placeholder='실패 시 알림받을 이메일'
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className='space-y-6'>
                  <FormField
                    control={form.control}
                    name='interval'
                    render={({ field }) => (
                      <FormItem className='space-y-3'>
                        <FormLabel>
                          실행 주기
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <RadioGroup
                            onValueChange={field.onChange}
                            defaultValue={field.value}
                            className='flex space-x-4'
                          >
                            <FormItem className='flex items-center space-y-0 space-x-2'>
                              <FormControl>
                                <RadioGroupItem value='daily' />
                              </FormControl>
                              <FormLabel className='font-normal'>
                                매일
                              </FormLabel>
                            </FormItem>
                            <FormItem className='flex items-center space-y-0 space-x-2'>
                              <FormControl>
                                <RadioGroupItem value='weekly' />
                              </FormControl>
                              <FormLabel className='font-normal'>
                                매주
                              </FormLabel>
                            </FormItem>
                            <FormItem className='flex items-center space-y-0 space-x-2'>
                              <FormControl>
                                <RadioGroupItem value='monthly' />
                              </FormControl>
                              <FormLabel className='font-normal'>
                                매월
                              </FormLabel>
                            </FormItem>
                          </RadioGroup>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name='startDate'
                    render={({ field }) => (
                      <FormItem className='flex flex-col'>
                        <FormLabel>
                          시작일
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <Popover>
                          <PopoverTrigger asChild>
                            <FormControl>
                              <Button
                                variant={'outline'}
                                className={cn(
                                  'w-full pl-3 text-left font-normal',
                                  !field.value && 'text-muted-foreground',
                                )}
                              >
                                {field.value ? (
                                  formatDate(field.value, 'yyyy년 MM월 dd일')
                                ) : (
                                  <span>날짜 선택</span>
                                )}
                                <CalendarIcon className='ml-auto h-4 w-4 opacity-50' />
                              </Button>
                            </FormControl>
                          </PopoverTrigger>
                          <PopoverContent className='w-auto p-0' align='start'>
                            <Calendar
                              mode='single'
                              selected={field.value}
                              onSelect={field.onChange}
                              disabled={date =>
                                date < new Date(new Date().setHours(0, 0, 0, 0))
                              }
                              initialFocus
                              locale={ko}
                            />
                          </PopoverContent>
                        </Popover>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name='endDate'
                    render={({ field }) => (
                      <FormItem className='flex flex-col'>
                        <FormLabel>
                          종료일
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <Popover>
                          <PopoverTrigger asChild>
                            <FormControl>
                              <Button
                                variant={'outline'}
                                className={cn(
                                  'w-full pl-3 text-left font-normal',
                                  !field.value && 'text-muted-foreground',
                                )}
                              >
                                {field.value ? (
                                  formatDate(field.value, 'yyyy년 MM월 dd일')
                                ) : (
                                  <span>날짜 선택</span>
                                )}
                                <CalendarIcon className='ml-auto h-4 w-4 opacity-50' />
                              </Button>
                            </FormControl>
                          </PopoverTrigger>
                          <PopoverContent className='w-auto p-0' align='start'>
                            <Calendar
                              mode='single'
                              selected={field.value}
                              onSelect={field.onChange}
                              disabled={date =>
                                date < new Date(new Date().setHours(0, 0, 0, 0))
                              }
                              initialFocus
                              locale={ko}
                            />
                          </PopoverContent>
                        </Popover>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name='executionTime'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          실행 시간
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <div className='relative'>
                            <Input
                              type='time'
                              placeholder='HH:MM (예: 09:00)'
                              {...field}
                            />
                          </div>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            </form>
          </Form>
        </ScrollArea>

        <DialogFooter className='mt-4 border-t pt-4'>
          <DialogClose asChild>
            <Button variant='outline' type='button'>
              취소
            </Button>
          </DialogClose>
          <Button
            type='button'
            onClick={form.handleSubmit(onSubmit)}
            disabled={form.formState.isSubmitting}
          >
            {form.formState.isSubmitting ? '생성 중...' : '생성하기'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default CreateScheduleModal;
