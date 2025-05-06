import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';

import { SaveJobRequest, useSaveJob } from '@/apis/job';
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
import { Form, FormControl, FormField, FormItem } from '@/components/ui/form';
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
import { JOB_TYPE } from '@/constant/job';
import { useJobStore } from '@/store/useJobStore';
import { TCommand } from '@/types/job';

const formSchema = z.object({
  jobType: z.nativeEnum(JOB_TYPE),
  jobName: z
    .string()
    .min(2, {
      message: 'JobName must be at least 2 characters.',
    })
    .max(20, {
      message: 'JobName must be at most 20 characters.',
    }),
  jobDescription: z
    .string()
    .min(2, {
      message: 'JobDescription must be at least 2 characters.',
    })
    .max(100, {
      message: 'JobDescription must be at most 100 characters.',
    }),
  sendEmail: z.boolean().default(false).optional(),
});

interface SaveJobDialogProps {
  sourceData: string;
  sourceDataCommand: string;
  commandList: TCommand[];
  code: string;
}

const SaveJobDialog: React.FC<SaveJobDialogProps> = ({
  sourceData,
  sourceDataCommand,
  commandList,
  code,
}) => {
  const { isEditMode, canSaveJob } = useJobStore();
  const jobMutation = useSaveJob();

  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      jobType: undefined,
      jobName: '',
      jobDescription: '',
      sendEmail: false,
    },
  });

  const onSubmit = async (values: z.infer<typeof formSchema>) => {
    // TODO: 이메일 전송
    const { jobType, jobName, jobDescription } = values;

    const request: SaveJobRequest = {
      type: jobType,
      name: jobName,
      description: jobDescription,
      data_load_command: sourceDataCommand,
      data_load_url: sourceData,
      commands: commandList.map(command => command.title),
      code,
    };

    const response = await jobMutation(request);

    console.log(response); // 추후 제거
  };

  return (
    <Dialog>
      <DialogTrigger>
        <Button variant={canSaveJob || !isEditMode ? 'default' : 'disabled'}>
          Save Job
        </Button>
      </DialogTrigger>

      <DialogContent>
        <DialogHeader>
          <DialogTitle className='pt-2 pb-4 text-center text-xl'>
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
                        <Select onValueChange={field.onChange} required>
                          <SelectTrigger className='w-full'>
                            <SelectValue placeholder='Job Type' />
                          </SelectTrigger>
                          <SelectContent>
                            {Object.values(JOB_TYPE).map((job, index) => (
                              <SelectItem key={`${job}-${index}`} value={job}>
                                {job}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </FormControl>
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
                          className='h-24'
                        />
                      </FormControl>
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
                  <Button type='submit' className='flex-1'>
                    Save
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
