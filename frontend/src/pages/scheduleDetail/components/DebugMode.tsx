import { AlertTriangle, CheckCircle2 } from 'lucide-react';

import { JobError } from '@/apis/schedulerMonitoring';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

interface DebugModeProps {
  jobs: JobError;
  jobTitle: string;
}

const DebugMode = ({ jobs, jobTitle }: DebugModeProps) => {
  if (!jobs) {
    return (
      <div className='flex items-center justify-center rounded-lg border border-gray-200 bg-white p-6 text-center shadow-sm'>
        <CheckCircle2 className='mr-2 h-5 w-5 text-green-500' />
        <p className='text-sm text-gray-600'>No error log provided.</p>
      </div>
    );
  }

  const errorMessageSummary = `${jobTitle.length > 70 ? jobTitle.substring(0, 70) + '...' : jobTitle}`;

  return (
    <Accordion type='single' collapsible className='w-full'>
      <AccordionItem value='item-1' className='rounded-lg border border-red-200 bg-red-50 shadow-sm'>
        <AccordionTrigger className='flex w-full items-center justify-between p-4 text-left text-sm font-medium text-red-700 hover:no-underline [&[data-state=open]>svg]:rotate-180'>
          <div className='flex items-center'>
            <AlertTriangle className='mr-2 h-4 w-4 flex-shrink-0' />
            <span>{errorMessageSummary}</span>
          </div>
        </AccordionTrigger>
        <AccordionContent className='p-4 pt-0 text-sm text-red-600'>
          <div className='space-y-3'>
            {jobs.error_type && (
              <p>
                <strong>Type:</strong> {jobs.error_type}
              </p>
            )}
            <p>
              <strong>Full Message:</strong> {jobs.error_message}
            </p>
            {jobs.error_trace && (
              <div className='mt-2 rounded bg-red-100 p-2'>
                <p className='mb-1 font-semibold'>Stack Trace:</p>
                <pre className='text-xs whitespace-pre-wrap'>{jobs.error_trace}</pre>
              </div>
            )}
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  );
};

export default DebugMode;
