import { Batch, Command, Job } from '@/types/scheduler';

interface DebugModeProps {
  schedule: Batch;
}

const DebugMode: React.FC<DebugModeProps> = ({ schedule }) => {
  let firstError: { job: Job; command: Command } | null = null;

  for (const job of schedule.jobList) {
    const errorCommand = job.commandList.find(
      cmd => cmd.commandStatus === 'error',
    );
    if (errorCommand) {
      firstError = { job, command: errorCommand };
      break; // Stop at the first error found
    }
  }

  return (
    // Apply sticky top to keep debug mode visible on scroll within its column
    <div className='sticky top-8 h-fit rounded-lg border border-gray-300 bg-white p-6 shadow-lg'>
      <h2 className='mb-6 text-center text-xl font-semibold text-gray-700'>
        Debug Mode
      </h2>
      <div className='space-y-4 text-sm text-gray-600'>
        {firstError ? (
          <>
            <p className='font-medium text-red-600'>
              Error occurred in Job: "{firstError.job.title}"
            </p>
            <p>Command "{firstError.command.commandTitle}" failed.</p>
            <p className='text-red-500'>
              <strong>Error Message:</strong> (Sample Error) Could not find
              column 'A'. Available columns are 'B', 'C', 'D'. Check data source
              or query.
            </p>
            <div className='mt-4 border-t pt-4'>
              <p className='font-semibold'>Suggestion:</p>
              <p className='text-blue-600'>
                (Sample Suggestion) Verify the column name 'A' exists in the
                output of the previous step or source. Consider using 'D' if
                appropriate.
              </p>
            </div>
          </>
        ) : (
          <p className='text-center text-green-600'>
            <svg
              xmlns='http://www.w3.org/2000/svg'
              className='mx-auto mb-2 h-8 w-8'
              fill='none'
              viewBox='0 0 24 24'
              stroke='currentColor'
              strokeWidth={2}
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                d='M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
              />
            </svg>
            No errors detected in this schedule run.
          </p>
        )}
      </div>
    </div>
  );
};

export default DebugMode;
