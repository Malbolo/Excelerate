import { ChevronRight, User } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

import { useGetLLMLogList } from '@/apis/agentMonitoring';
import CustomPagination from '@/components/Pagination';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import useInternalRouter from '@/hooks/useInternalRouter';
import { formatDateTime } from '@/lib/dateFormat';
import { useLocalDate } from '@/store/useLocalDate';

const AgentCallList = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { push } = useInternalRouter();
  const { locale, place } = useLocalDate();

  const { data } = useGetLLMLogList({
    user_name: searchParams.get('name') || '',
    start_date: searchParams.get('startDate') || '',
    end_date: searchParams.get('endDate') || '',
    page: searchParams.get('page') || '1',
    size: '4',
  });
  const { logs, pages } = data;

  const handleLogClick = (logId: string) => {
    setSearchParams(prev => {
      prev.set('logId', logId);
      return prev;
    });
    push(`?${searchParams.toString()}`);
  };

  return (
    <div className='flex h-full w-full flex-col justify-between gap-5'>
      <section className='grid h-full w-full grid-cols-1 grid-rows-4 gap-2'>
        {logs.map(log => (
          <Card
            key={`${log.log_id}-${log.created_at}`}
            onClick={() => handleLogClick(log.log_id)}
            className='group flex w-full flex-1 cursor-pointer justify-between transition-all'
          >
            <CardHeader>
              <div className='flex items-center justify-between'>
                <CardTitle className='text-md font-bold text-slate-800'>{log.agent_name}</CardTitle>
                <Badge variant='outline'>{formatDateTime(log.created_at, locale, place)}</Badge>
              </div>
              <CardDescription className='line-clamp-2 text-xs text-slate-600'>{log.log_detail}</CardDescription>
            </CardHeader>
            <CardContent className='flex items-center gap-2 pt-0'>
              <div className='flex items-center gap-2'>
                <User className='h-4 w-4' />
                <span className='text-xs font-medium text-slate-700'>{log.user_name}</span>
              </div>
              <Badge
                variant='secondary'
                className='ml-auto h-6 w-6 rounded-full p-0 transition-all ease-in-out group-hover:scale-105'
              >
                <ChevronRight className='h-4 w-4' />
              </Badge>
            </CardContent>
          </Card>
        ))}
      </section>
      <CustomPagination totalPages={pages} />
    </div>
  );
};

export default AgentCallList;
