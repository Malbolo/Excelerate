import { useEffect, useState } from 'react';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useParams } from 'react-router-dom';
import ClipLoader from 'react-spinners/ClipLoader';
import { z } from 'zod';

import { SaveJobRequest, useEditJob, useSaveJob } from '@/apis/job';
import { useGetJobDetail } from '@/apis/jobManagement';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { JOB_TYPES_CONFIG } from '@/constant/job';
import { useCommandStore } from '@/store/useCommandStore';
import { useJobResultStore } from '@/store/useJobResultStore';
import { useJobStore } from '@/store/useJobStore';
import { useSourceStore } from '@/store/useSourceStore';
import { JobType } from '@/types/job';

const formSchema = z.object({
  jobType: z.custom<JobType>(),
  jobName: z
    .string()
    .min(2, {
      message: 'Job name must be at least 2 characters.',
    })
    .max(20, {
      message: 'Job name must be at most 20 characters.',
    }),
  jobDescription: z
    .string()
    .min(2, {
      message: 'Job description must be at least 2 characters.',
    })
    .max(100, {
      message: 'Job description must be at most 100 characters.',
    }),
  sendEmail: z.boolean().default(false).optional(),
});

const SaveJobDialog: React.FC = () => {
  const { jobId } = useParams();

  const [open, setOpen] = useState(false);

  const { sourceDataCommand, sourceDataUrl } = useSourceStore();
  const { commandList } = useCommandStore();
  const { code } = useJobResultStore();
  const { isEditMode, canSaveJob } = useJobStore();

  const { mutateAsync: saveJobMutation, isPending: isJobSaving } = useSaveJob();
  const { mutateAsync: editJobMutation, isPending: isJobEditing } =
    useEditJob();

  const getJobDetail = useGetJobDetail();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      jobType: undefined,
      jobName: '',
      jobDescription: '',
      sendEmail: false,
    },
  });

  useEffect(() => {
    const fetchJobDetail = async () => {
      if (!jobId) return;

      const data = await getJobDetail(jobId);

      form.reset({
        jobType: data.type,
        jobName: data.title,
        jobDescription: data.description,
        sendEmail: false,
      });
    };

    fetchJobDetail();
  }, []);

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    const { jobType, jobName, jobDescription } = values;
    const request: SaveJobRequest = {
      type: jobType,
      title: jobName,
      description: jobDescription,
      data_load_command: sourceDataCommand,
      data_load_url: sourceDataUrl,
      commands: commandList.map(({ content }) => content),
      code,
    };

    if (jobId) await editJobMutation({ request, jobId });
    else await saveJobMutation(request);

    setOpen(false);
    form.reset();
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger disabled={!canSaveJob || isEditMode}>
        <Button disabled={!canSaveJob || isEditMode}>Save Job</Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle className='pt-2 pb-4 text-center text-xl font-bold'>
            Save Job
          </DialogTitle>
          <DialogDescription className='flex flex-col'>
            <Form {...form}>
              <form
                onSubmit={form.handleSubmit(onSubmit)}
                className='flex flex-col gap-3'
              >
                <FormField
                  control={form.control}
                  name='jobType'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Select
                          onValueChange={field.onChange}
                          value={field.value}
                          required
                        >
                          <SelectTrigger className='w-full'>
                            <SelectValue placeholder='Job Type' />
                          </SelectTrigger>
                          <SelectContent>
                            {JOB_TYPES_CONFIG.map((job, index) => (
                              <SelectItem
                                key={`${job.id}-${index}`}
                                value={job.id}
                              >
                                {job.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='jobName'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Input
                          placeholder='Job Name'
                          value={field.value}
                          onChange={field.onChange}
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='jobDescription'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <Textarea
                          placeholder='Job Description'
                          value={field.value}
                          onChange={field.onChange}
                          className='h-24 resize-none'
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name='sendEmail'
                  render={({ field }) => (
                    <FormItem>
                      <FormControl>
                        <div className='flex items-center gap-2'>
                          <Checkbox
                            id='send-email'
                            checked={field.value}
                            onCheckedChange={field.onChange}
                            className='cursor-pointer'
                          />
                          <Label htmlFor='send-email'>
                            Would you like to receive the job detail via email?
                          </Label>
                        </div>
                      </FormControl>
                    </FormItem>
                  )}
                />

                <DialogFooter className='mt-4'>
                  <DialogClose asChild>
                    <Button variant='outline' className='flex-1'>
                      Cancel
                    </Button>
                  </DialogClose>
                  <Button
                    type='submit'
                    className='flex-1'
                    disabled={isJobSaving || isJobEditing}
                  >
                    {isJobSaving || isJobEditing ? (
                      <ClipLoader size={18} color='white' />
                    ) : (
                      'Save'
                    )}
                  </Button>
                </DialogFooter>
              </form>
            </Form>
          </DialogDescription>
        </DialogHeader>
      </DialogContent>
    </Dialog>
  );
};

export default SaveJobDialog;
