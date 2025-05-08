import { CheckCircle, Clock, HelpCircle, XCircle } from 'lucide-react';

const StatusIcon = ({ status }: { status: string }) => {
  switch (status) {
    case 'success':
      return <CheckCircle className='z-50 h-5 w-5 text-green-500' />;
    case 'failed':
      return <XCircle className='z-50 h-5 w-5 text-red-500' />;
    case 'pending':
      return <Clock className='z-50 h-5 w-5 text-yellow-500' />;
    default:
      return <HelpCircle className='z-50 h-5 w-5 text-gray-400' />;
  }
};

export default StatusIcon;
