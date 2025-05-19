import { useQueryClient } from '@tanstack/react-query';
import { LogOut } from 'lucide-react';
import { toast } from 'sonner';

import useInternalRouter from '@/hooks/useInternalRouter';
import { cn } from '@/lib/utils';

import { Button } from '../ui/button';

interface LogoutButtonProps {
  name: string;
  isCollapsed?: boolean;
}

const LogoutButton = ({ name, isCollapsed }: LogoutButtonProps) => {
  const queryClient = useQueryClient();
  const { replace } = useInternalRouter();

  const handleLogoutClick = () => {
    localStorage.removeItem('token');
    toast.success('Logout completed successfully.');
    queryClient.resetQueries();
    replace('/');
  };

  return (
    <div className={cn('flex flex-col gap-3', isCollapsed ? 'items-center' : 'items-stretch')}>
      {!isCollapsed && <span className='text-center text-sm text-gray-800'>Hello, {name}!</span>}
      <Button
        variant='outline'
        size='sm'
        className='w-full'
        onClick={handleLogoutClick}
        title={isCollapsed ? 'Logout' : undefined}
      >
        {isCollapsed ? <LogOut className='h-5 w-5' /> : 'Logout'}
      </Button>
    </div>
  );
};

export default LogoutButton;
