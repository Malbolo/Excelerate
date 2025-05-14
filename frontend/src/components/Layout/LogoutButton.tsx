import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import useInternalRouter from '@/hooks/useInternalRouter';

import { Button } from '../ui/button';

interface LogoutButtonProps {
  name: string;
}

const LogoutButton = ({ name }: LogoutButtonProps) => {
  const queryClient = useQueryClient();
  const { replace } = useInternalRouter();

  const handleLogoutClick = () => {
    localStorage.removeItem('token');
    toast.success('Logout completed successfully.');
    queryClient.resetQueries();
    replace('/');
  };

  return (
    <div className='flex flex-col items-center gap-3'>
      <span className='text-sm text-gray-800'>Hello, {name}!</span>
      <Button
        variant='outline'
        size='sm'
        className='w-full'
        onClick={handleLogoutClick}
      >
        Logout
      </Button>
    </div>
  );
};

export default LogoutButton;
