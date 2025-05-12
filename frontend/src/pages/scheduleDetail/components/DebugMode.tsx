import { CheckCircleIcon } from 'lucide-react';

import { JobError } from '@/apis/schedulerMonitoring';

interface DebugModeProps {
  error: JobError;
}

const DebugMode = ({ error }: DebugModeProps) => {
  if (!error) return null;

  const { error_message, error_time } = error;

  return (
    <div className='sticky top-8 h-fit rounded-lg border border-gray-300 bg-white p-6 shadow-lg'>
      <h2 className='mb-6 text-center text-xl font-semibold text-gray-700'>
        Debug Mode
      </h2>
      <div className='space-y-4 text-sm text-gray-600'>
        {error_message ? (
          <>
            <div className='flex items-center justify-between'>
              <p className='font-medium text-red-600'>Error Details</p>
              <p className='text-xs text-gray-500'>
                {new Date(error_time).toLocaleString()}
              </p>
            </div>
            <p className='text-red-500'>
              <strong>Error Message:</strong> {error_message}
            </p>
            {/* {error_trace && (
              <div className='mt-4 rounded-md bg-gray-50 p-4'>
                <p className='mb-2 font-semibold'>Stack Trace:</p>
                <pre className='text-xs whitespace-pre-wrap'>{error_trace}</pre>
              </div>
            )} */}
          </>
        ) : (
          <p className='text-center text-green-600'>
            <CheckCircleIcon className='mx-auto mb-2 h-8 w-8' />
            No errors detected in this schedule run.
          </p>
        )}
      </div>
    </div>
  );
};

export default DebugMode;
