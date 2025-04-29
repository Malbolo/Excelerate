import { CheckCircleIcon } from 'lucide-react';

import { Command, Job, Schedule } from '@/types/scheduler';

interface DebugModeProps {
  schedule: Schedule;
}

// todo: 더미데이터이기에 실제 변경 예정
const DebugMode = ({ schedule }: DebugModeProps) => {
  let firstError: { job: Job; command: Command } | null = null;

  for (const job of schedule.jobList) {
    const errorCommand = job.commandList.find(
      cmd => cmd.commandStatus === 'error',
    );
    if (errorCommand) {
      firstError = { job, command: errorCommand };
      break;
    }
  }

  return (
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
            <CheckCircleIcon className='mx-auto mb-2 h-8 w-8' />
            No errors detected in this schedule run.
          </p>
        )}
      </div>
    </div>
  );
};

export default DebugMode;
