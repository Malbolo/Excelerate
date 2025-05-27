import { z } from 'zod';

const createScheduleSchema = z
  .object({
    title: z.string().min(1, 'Please enter a schedule title.'),
    description: z.string().min(1, 'Please enter a description.'),
    success_emails: z
      .array(z.string().email({ message: 'Please enter a valid email address.' }))
      .min(1, 'Please add at least one success notification email.'),
    failure_emails: z
      .array(z.string().email({ message: 'Please enter a valid email address.' }))
      .min(1, 'Please add at least one failure notification email.'),
    frequency: z.enum(['daily', 'weekly', 'monthly'], {
      required_error: 'Please select an execution interval.',
    }),
    start_date: z.date({
      required_error: 'Please select a start date.',
    }),
    end_date: z.date({
      required_error: 'Please select an end date.',
    }),
    execution_time: z.string().regex(/^([01]\d|2[0-3]):([0-5]\d)$/, {
      message: 'Please enter the time in HH:MM format (e.g., 09:00, 14:30).',
    }),
  })
  .refine(
    data => {
      if (data.start_date && data.end_date) {
        const start = new Date(data.start_date.setHours(0, 0, 0, 0));
        const end = new Date(data.end_date.setHours(0, 0, 0, 0));
        return end >= start;
      }
      return true;
    },
    {
      message: 'End date must be the same as or later than the start date.',
      path: ['end_date'],
    },
  );

export type CreateScheduleFormData = z.infer<typeof createScheduleSchema>;

export { createScheduleSchema };
