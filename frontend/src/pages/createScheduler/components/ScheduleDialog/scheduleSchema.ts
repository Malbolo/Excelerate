import { z } from 'zod';

const createScheduleSchema = z
  .object({
    scheduleTitle: z.string().min(1, 'Please enter a schedule title.'),
    scheduleDescription: z.string().min(1, 'Please enter a description.'),
    successEmail: z
      .array(
        z.string().email({ message: 'Please enter a valid email address.' }),
      )
      .min(1, 'Please add at least one success notification email.'),
    failEmail: z
      .array(
        z.string().email({ message: 'Please enter a valid email address.' }),
      )
      .min(1, 'Please add at least one failure notification email.'),
    interval: z.enum(['daily', 'weekly', 'monthly'], {
      required_error: 'Please select an execution interval.',
    }),
    startDate: z.date({
      required_error: 'Please select a start date.',
    }),
    endDate: z.date({
      required_error: 'Please select an end date.',
    }),
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

export type CreateScheduleFormData = z.infer<typeof createScheduleSchema>;

export { createScheduleSchema };
