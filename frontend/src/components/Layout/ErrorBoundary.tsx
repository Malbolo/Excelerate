import { AlertCircle, Home } from 'lucide-react';
import { useRouteError } from 'react-router-dom';

import useInternalRouter from '@/hooks/useInternalRouter';

import { Button } from '../ui/button';

const ErrorBoundary = () => {
  const error = useRouteError();
  const { replace } = useInternalRouter();

  return (
    <div className='bg-gradient flex min-h-screen w-full flex-col items-center justify-center p-4'>
      <div className='bg-card w-full max-w-md rounded-xl border p-8 shadow-sm'>
        <div className='flex flex-col items-center gap-6'>
          <div className='bg-destructive/10 rounded-full p-4'>
            <AlertCircle className='text-destructive h-8 w-8' />
          </div>

          <div className='text-center'>
            <h2 className='text-foreground text-xl font-bold'>An Error Occurred</h2>
            <p className='text-muted-foreground mt-1 text-sm'>
              We apologize for the inconvenience.
              <br />
              Please try again later.
            </p>
          </div>

          <div className='bg-muted w-full rounded-lg p-4'>
            <p className='text-muted-foreground text-center text-sm'>
              {error instanceof Error ? error.message : 'An unexpected error has occurred.'}
            </p>
          </div>

          <Button onClick={() => replace('/')}>
            <Home className='h-4 w-4' />
            Go to Main Page
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ErrorBoundary;
