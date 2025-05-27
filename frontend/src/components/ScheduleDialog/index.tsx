import { Dispatch, useState } from 'react';

import { zodResolver } from '@hookform/resolvers/zod';
import { format as formatDate } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { CalendarIcon, X } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { toast } from 'sonner';
import { z } from 'zod';

import { JobManagement } from '@/apis/jobManagement';
import { Schedule, useCreateSchedule, useUpdateSchedule } from '@/apis/schedulerManagement';
import { Badge } from '@/components/ui/badge';
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
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

import { CreateScheduleFormData, createScheduleSchema } from './scheduleSchema';

interface ScheduleDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  selectedJobs: JobManagement[];
  scheduleDetail?: Schedule;
}

const ScheduleDialog = ({ isOpen, onOpenChange, selectedJobs, scheduleDetail }: ScheduleDialogProps) => {
  const isEditMode = !!scheduleDetail;

  const [currentSuccessEmail, setCurrentSuccessEmail] = useState('');
  const [currentFailEmail, setCurrentFailEmail] = useState('');

  const editSchedule = useUpdateSchedule();
  const createSchedule = useCreateSchedule();

  const form = useForm<CreateScheduleFormData>({
    resolver: zodResolver(createScheduleSchema),
    defaultValues: {
      title: isEditMode ? scheduleDetail.title : '',
      description: isEditMode ? scheduleDetail.description : '',
      success_emails: isEditMode ? scheduleDetail.success_emails : [],
      failure_emails: isEditMode ? scheduleDetail.failure_emails : [],
      frequency: isEditMode ? scheduleDetail.frequency : 'daily',
      start_date: isEditMode ? new Date(scheduleDetail.start_date) : new Date(),
      end_date: isEditMode ? new Date(scheduleDetail.end_date) : new Date(2099, 11, 31),
      execution_time: isEditMode ? scheduleDetail.execution_time : '',
    },
  });

  const onSubmit = (values: CreateScheduleFormData) => {
    const k_startDate = new Date(
      values.start_date.getFullYear(),
      values.start_date.getMonth(),
      values.start_date.getDate(),
      parseInt(values.execution_time.split(':')[0]),
      parseInt(values.execution_time.split(':')[1]),
      0,
    );

    const k_endDate = new Date(
      values.end_date.getFullYear(),
      values.end_date.getMonth(),
      values.end_date.getDate(),
      0,
      0,
      0,
    );

    const server_start_date = k_startDate.toISOString().split('.')[0];
    const server_execution_time = server_start_date.substring(11, 16);
    const server_end_date = k_endDate.toISOString().split('.')[0];

    const submissionData = JSON.stringify({
      ...values,
      jobs: selectedJobs.map((job, index) => ({
        id: String(job.id),
        order: index + 1,
      })),
      start_date: server_start_date,
      end_date: server_end_date,
      execution_time: server_execution_time,
    });

    if (isEditMode && scheduleDetail) {
      editSchedule({
        scheduleId: scheduleDetail.schedule_id,
        schedule: submissionData,
      });
    } else {
      createSchedule({ schedule: submissionData });
    }

    onOpenChange(false);
    form.reset();
    setCurrentSuccessEmail('');
    setCurrentFailEmail('');
  };

  const handleOpenChange = (open: boolean) => {
    onOpenChange(open);
    if (!open) {
      form.reset();
      setCurrentSuccessEmail('');
      setCurrentFailEmail('');
    }
  };

  const handleAddEmail = (
    emailValue: string,
    setEmailValue: Dispatch<React.SetStateAction<string>>,
    fieldName: 'success_emails' | 'failure_emails',
  ) => {
    if (emailValue.trim() === '') return;
    const emailCheck = z.string().email().safeParse(emailValue);
    if (!emailCheck.success) {
      toast.error('Invalid email format');
      return;
    }

    const currentEmails = form.getValues(fieldName) || [];
    if (currentEmails.includes(emailValue)) {
      toast.error(`Email "${emailValue}" already added.`);
      return;
    }
    form.setValue(fieldName, [...currentEmails, emailValue], {
      shouldValidate: true,
    });
    setEmailValue('');
  };

  const handleRemoveEmail = (emailToRemove: string, fieldName: 'success_emails' | 'failure_emails') => {
    const currentEmails = form.getValues(fieldName) || [];
    form.setValue(
      fieldName,
      currentEmails.filter(email => email !== emailToRemove),
      { shouldValidate: true },
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleOpenChange}>
      <DialogContent className='flex max-h-[calc(100vh-80px)] flex-col sm:max-w-4xl'>
        <DialogHeader>
          <DialogTitle className='text-lg font-bold'>{isEditMode ? 'Edit Schedule' : 'Create Schedule'}</DialogTitle>
          <DialogDescription className='text-sm'>
            {isEditMode
              ? `Edit the schedule for the selected ${selectedJobs.length} Jobs.`
              : `Create a new schedule for the selected ${selectedJobs.length} Jobs.`}
          </DialogDescription>
        </DialogHeader>

        <section className='h-full overflow-y-auto pr-6'>
          <div className='card-gradient mb-4 rounded-md border p-3'>
            <Badge variant='secondary' className='mb-2 text-xs'>
              {selectedJobs.length} Selected Jobs
            </Badge>
            <ul className='max-h-24 list-inside list-decimal space-y-1 overflow-y-auto text-xs text-gray-600'>
              {selectedJobs.map(job => (
                <li key={job.id}>{job.title}</li>
              ))}
            </ul>
          </div>

          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className='space-y-4'>
              <div className='grid grid-cols-1 gap-x-8 gap-y-6 md:grid-cols-2'>
                <div className='space-y-6'>
                  {/* 스케줄 제목 */}
                  <FormField
                    control={form.control}
                    name='title'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className='font-bold'>
                          Schedule Title <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input placeholder='e.g., Daily Sales Data Aggregation' {...field} />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* 스케줄 설명 */}
                  <FormField
                    control={form.control}
                    name='description'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className='font-bold'>
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

                  {/* 성공 알림 이메일 */}
                  <FormField
                    control={form.control}
                    name='success_emails'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className='font-bold'>
                          Success Notification Email <span className='text-red-500'>*</span>
                        </FormLabel>
                        <div className='flex items-center gap-2'>
                          <FormControl>
                            <Input
                              type='email'
                              placeholder='Enter email and press Add'
                              value={currentSuccessEmail}
                              onChange={e => setCurrentSuccessEmail(e.target.value)}
                              onKeyDown={e => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  handleAddEmail(currentSuccessEmail, setCurrentSuccessEmail, 'success_emails');
                                }
                              }}
                            />
                          </FormControl>
                          <Button
                            type='button'
                            variant='outline'
                            onClick={() =>
                              handleAddEmail(currentSuccessEmail, setCurrentSuccessEmail, 'success_emails')
                            }
                          >
                            Add
                          </Button>
                        </div>
                        <FormMessage />
                        <div className='mt-2 flex flex-wrap gap-1'>
                          {field.value &&
                            field.value.map((email, index) => (
                              <Badge key={index} variant='secondary'>
                                {email}
                                <button
                                  type='button'
                                  className='text-destructive-foreground ml-1.5 rounded-full p-0.5 opacity-70 hover:opacity-100'
                                  onClick={() => handleRemoveEmail(email, 'success_emails')}
                                >
                                  <X className='h-3 w-3' />
                                </button>
                              </Badge>
                            ))}
                        </div>
                      </FormItem>
                    )}
                  />

                  {/* 실패 알림 이메일 */}
                  <FormField
                    control={form.control}
                    name='failure_emails'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className='font-bold'>
                          Failure Notification Email <span className='text-red-500'>*</span>
                        </FormLabel>
                        <div className='flex items-center gap-2'>
                          <FormControl>
                            <Input
                              type='email'
                              placeholder='Enter email and press Add'
                              value={currentFailEmail}
                              onChange={e => setCurrentFailEmail(e.target.value)}
                              onKeyDown={e => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  handleAddEmail(currentFailEmail, setCurrentFailEmail, 'failure_emails');
                                }
                              }}
                            />
                          </FormControl>
                          <Button
                            type='button'
                            variant='outline'
                            onClick={() => handleAddEmail(currentFailEmail, setCurrentFailEmail, 'failure_emails')}
                          >
                            Add
                          </Button>
                        </div>
                        <FormMessage />
                        <div className='mt-2 flex flex-wrap gap-1'>
                          {field.value &&
                            field.value.map((email, index) => (
                              <Badge key={index} variant='secondary'>
                                {email}
                                <button
                                  type='button'
                                  className='text-destructive-foreground ml-1.5 rounded-full p-0.5 opacity-70 hover:opacity-100'
                                  onClick={() => handleRemoveEmail(email, 'failure_emails')}
                                >
                                  <X className='h-3 w-3' />
                                </button>
                              </Badge>
                            ))}
                        </div>
                      </FormItem>
                    )}
                  />
                </div>

                {/* 실행 간격 */}
                <div className='space-y-6'>
                  <FormField
                    control={form.control}
                    name='frequency'
                    render={({ field }) => (
                      <FormItem className='space-y-3'>
                        <FormLabel className='font-bold'>
                          Execution Interval
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
                              <FormLabel className='font-normal'>Daily</FormLabel>
                            </FormItem>
                            <FormItem className='flex items-center space-y-0 space-x-2'>
                              <FormControl>
                                <RadioGroupItem value='weekly' />
                              </FormControl>
                              <FormLabel className='font-normal'>Weekly</FormLabel>
                            </FormItem>
                            <FormItem className='flex items-center space-y-0 space-x-2'>
                              <FormControl>
                                <RadioGroupItem value='monthly' />
                              </FormControl>
                              <FormLabel className='font-normal'>Monthly</FormLabel>
                            </FormItem>
                          </RadioGroup>
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* 실행 시작 날짜 */}
                  <FormField
                    control={form.control}
                    name='start_date'
                    render={({ field }) => (
                      <FormItem className='flex flex-col'>
                        <FormLabel className='font-bold'>
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
                                {formatDate(field.value, 'MMM d, yyyy', {
                                  locale: enUS,
                                })}
                                <CalendarIcon className='ml-auto h-4 w-4 opacity-50' />
                              </Button>
                            </PopoverTrigger>
                          </FormControl>
                          <PopoverContent className='w-auto p-0' align='start'>
                            <Calendar
                              mode='single'
                              selected={field.value}
                              onSelect={field.onChange}
                              disabled={date => new Date(date) < new Date()}
                              initialFocus
                              locale={enUS}
                            />
                          </PopoverContent>
                        </Popover>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  {/* 실행 종료 날짜 */}
                  <FormField
                    control={form.control}
                    name='end_date'
                    render={({ field }) => (
                      <FormItem className='flex flex-col'>
                        <FormLabel className='font-bold'>
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
                                {formatDate(field.value, 'MMM d, yyyy', {
                                  locale: enUS,
                                })}
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
                                const selectedDate = new Date(date);
                                const startDate = new Date(form.getValues('start_date'));
                                return selectedDate < startDate;
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

                  {/* 실행 시간 */}
                  <FormField
                    control={form.control}
                    name='execution_time'
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className='font-bold'>
                          Execution Time <span className='text-red-500'>*</span>
                        </FormLabel>
                        <FormControl>
                          <Input type='time' placeholder='HH:MM (e.g., 09:00)' {...field} />
                        </FormControl>
                        <FormDescription>Time the schedule will run (HH:MM format).</FormDescription>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>
              </div>
            </form>
          </Form>
        </section>

        <DialogFooter className='mt-4 pt-4'>
          <DialogClose asChild>
            <Button variant='outline' type='button'>
              Cancel
            </Button>
          </DialogClose>
          <Button type='button' onClick={form.handleSubmit(onSubmit)}>
            {isEditMode ? 'Update' : 'Create'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ScheduleDialog;
