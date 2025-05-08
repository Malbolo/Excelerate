import { zodResolver } from '@hookform/resolvers/zod';
import { format as formatDate } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { CalendarIcon } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { JobResponse } from '@/apis/jobManagement';
import {
  ScheduleDetailResponse,
  useCreateSchedule,
} from '@/apis/schedulerManagement';
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
  FormDescription,
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

export interface EditScheduleFormData {
  scheduleTitle: string;
  scheduleDescription: string;
  successEmail: string;
  failEmail: string;
  interval: 'daily' | 'weekly' | 'monthly';
  startDate: Date;
  endDate: Date | undefined;
  executionTime: string;
  selectedJobs: JobResponse[];
}

const formSchema = z
  .object({
    scheduleTitle: z.string().min(1, 'Please enter a schedule title.'),
    scheduleDescription: z.string().min(1, 'Please enter a description.'),
    successEmail: z
      .string()
      .min(1, 'Please enter a success notification email.')
      .email({ message: 'Please enter a valid email address.' }),
    failEmail: z
      .string()
      .min(1, 'Please enter a failure notification email.')
      .email({ message: 'Please enter a valid email address.' }),
    interval: z.enum(['daily', 'weekly', 'monthly'], {
      required_error: 'Please select an execution interval.',
    }),
    startDate: z.date({
      required_error: 'Please select a start date.',
    }),
    endDate: z.date().optional(),
    executionTime: z.string().regex(/^([01]\d|2[0-3]):([0-5]\d)$/, {
      message: 'Please enter the time in HH:MM format (e.g., 09:00, 14:30).',
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
      message: 'End date must be the same as or later than the start date.',
      path: ['endDate'],
    },
  );

interface EditScheduleModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  selectedJobs: JobResponse[];
  scheduleDetail: ScheduleDetailResponse;
}

const EditScheduleModal = ({
  isOpen,
  onOpenChange,
  selectedJobs,
  scheduleDetail,
}: EditScheduleModalProps) => {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      scheduleTitle: scheduleDetail.title,
      scheduleDescription: scheduleDetail.description,
      successEmail: scheduleDetail.success_emails[0],
      failEmail: scheduleDetail.failure_emails[0],
      interval: scheduleDetail.frequency as 'daily' | 'weekly' | 'monthly',
      startDate: new Date(scheduleDetail.start_date),
      endDate: scheduleDetail.end_date
        ? new Date(scheduleDetail.end_date)
        : undefined,
      executionTime: scheduleDetail.execution_time,
    },
  });

  const createSchedule = useCreateSchedule();

  async function onSubmit(values: z.infer<typeof formSchema>) {
    const finalEndDate =
      values.endDate instanceof Date ? values.endDate : new Date(2099, 11, 31);

    const submissionData = {
      ...values,
      endDate: finalEndDate,
      selectedJobs,
    };

    // 스케쥴 생성
    createSchedule(submissionData);

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
          <DialogTitle>Create New Schedule</DialogTitle>
          <DialogDescription>
            Configure the new schedule for the selected {selectedJobs.length}{' '}
            JOBs. (All fields required)
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className='flex-grow pr-6'>
          <div className='mb-4 rounded-md border bg-gray-50 p-3'>
            <h4 className='mb-2 text-sm font-medium text-gray-700'>
              Selected JOBs ({selectedJobs.length}):
            </h4>
            <ul className='max-h-24 list-inside list-decimal space-y-1 overflow-y-auto text-xs text-gray-600'>
              {selectedJobs.map(job => (
                <li key={job.id}>{job.title}</li>
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
                    name='scheduleTitle'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          Schedule Title <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input
                            placeholder='e.g., Daily Sales Data Aggregation'
                            {...field}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                  <FormField
                    control={form.control}
                    name='scheduleDescription'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>
                          Description <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Textarea
                            placeholder='Enter a description for the schedule.'
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
                          Success Notification Email{' '}
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type='email'
                            placeholder='Email address for success notification'
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
                          Failure Notification Email{' '}
                          <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type='email'
                            placeholder='Email address for failure notification'
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
                          Execution Interval{' '}
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
                                Daily
                              </FormLabel>
                            </FormItem>
                            <FormItem className='flex items-center space-y-0 space-x-2'>
                              <FormControl>
                                <RadioGroupItem value='weekly' />
                              </FormControl>
                              <FormLabel className='font-normal'>
                                Weekly
                              </FormLabel>
                            </FormItem>
                            <FormItem className='flex items-center space-y-0 space-x-2'>
                              <FormControl>
                                <RadioGroupItem value='monthly' />
                              </FormControl>
                              <FormLabel className='font-normal'>
                                Monthly
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
                          Start Date <span className='text-red-500'>*</span>
                        </FormLabel>
                        <Popover>
                          <FormControl>
                            <PopoverTrigger asChild={false}>
                              <Button
                                type='button'
                                variant={'outline'}
                                className={cn(
                                  'w-full pl-3 text-left font-normal',
                                  !field.value && 'text-muted-foreground',
                                )}
                              >
                                {field.value ? (
                                  formatDate(field.value, 'MMM d, yyyy', {
                                    locale: enUS,
                                  })
                                ) : (
                                  <span>Select date</span>
                                )}
                                <CalendarIcon className='ml-auto h-4 w-4 opacity-50' />
                              </Button>
                            </PopoverTrigger>
                          </FormControl>
                          <PopoverContent className='w-auto p-0' align='start'>
                            <Calendar
                              mode='single'
                              selected={field.value}
                              onSelect={field.onChange}
                              disabled={date =>
                                date < new Date(new Date().setHours(0, 0, 0, 0))
                              }
                              initialFocus
                              locale={enUS}
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
                          End Date <span className='text-red-500'>*</span>
                        </FormLabel>
                        <Popover>
                          <FormControl>
                            <PopoverTrigger asChild={false}>
                              <Button
                                type='button'
                                variant={'outline'}
                                className={cn(
                                  'w-full pl-3 text-left font-normal',
                                  !field.value && 'text-muted-foreground',
                                )}
                              >
                                {field.value ? (
                                  formatDate(field.value, 'MMM d, yyyy', {
                                    locale: enUS,
                                  })
                                ) : (
                                  <span>Select date</span>
                                )}
                                <CalendarIcon className='ml-auto h-4 w-4 opacity-50' />
                              </Button>
                            </PopoverTrigger>
                          </FormControl>
                          <PopoverContent className='w-auto p-0' align='start'>
                            <Calendar
                              mode='single'
                              selected={field.value}
                              onSelect={field.onChange}
                              disabled={date => {
                                const start = form.getValues('startDate');
                                const today = new Date(
                                  new Date().setHours(0, 0, 0, 0),
                                );
                                if (start && date < start) return true;
                                if (date < today) return true;
                                return false;
                              }}
                              initialFocus
                              locale={enUS}
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
                          Execution Time <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input
                            type='time'
                            placeholder='HH:MM (e.g., 09:00)'
                            {...field}
                          />
                        </FormControl>
                        <FormDescription>
                          Time the schedule will run (HH:MM format).
                        </FormDescription>
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
              Cancel
            </Button>
          </DialogClose>
          <Button
            type='button'
            onClick={form.handleSubmit(onSubmit)}
            disabled={form.formState.isSubmitting}
          >
            {form.formState.isSubmitting ? 'Creating...' : 'Create'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default EditScheduleModal;
