import { CheckCircle, Clock, HelpCircle, XCircle } from 'lucide-react';

import { Status } from '@/types/job';

const StatusIcon = ({ status }: { status: Status }) => {
  switch (status) {
    case 'success':
      return <CheckCircle className='text-success z-50 h-4 w-4' />;
    case 'failed':
      return <XCircle className='text-destructive z-50 h-4 w-4' />;
    case 'pending':
      return <Clock className='z-50 h-4 w-4 text-yellow-500' />;
    default:
      return <HelpCircle className='z-50 h-4 w-4 text-gray-400' />;
  }
};

export default StatusIcon;
