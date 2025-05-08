import { AlertCircle, Home } from 'lucide-react';
import { useRouteError } from 'react-router-dom';

import useInternalRouter from '@/hooks/useInternalRouter';

const ErrorBoundary = () => {
  const error = useRouteError();
  const { replace } = useInternalRouter();

  return (
    <div className='flex min-h-screen w-full flex-col items-center justify-center bg-gray-50 p-4'>
      <div className='w-full max-w-md rounded-lg bg-white p-8 shadow-lg'>
        <div className='flex flex-col items-center gap-4'>
          <div className='rounded-full bg-red-100 p-3'>
            <AlertCircle className='h-8 w-8 text-red-600' />
          </div>

          <h2 className='text-2xl font-bold text-gray-900'>
            오류가 발생했습니다
          </h2>

          <div className='w-full rounded-md bg-gray-50 p-4 text-center'>
            <p className='text-gray-600'>
              {error instanceof Error
                ? error.message
                : '알 수 없는 에러가 발생했습니다.'}
            </p>
          </div>

          <button
            onClick={() => replace('/')}
            className='mt-2 flex items-center gap-2 rounded-md bg-blue-500 px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-blue-600 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:outline-none'
          >
            <Home className='h-4 w-4' />
            Go to Main Page
          </button>
        </div>
      </div>
    </div>
  );
};

export default ErrorBoundary;
