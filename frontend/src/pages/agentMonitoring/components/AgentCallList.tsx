import { ChevronRight, User } from 'lucide-react';
import { useLocation, useSearchParams } from 'react-router-dom';

import { useGetJobList } from '@/apis/agentMonitoring';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import useInternalRouter from '@/hooks/useInternalRouter';
import { formatDateTime } from '@/lib/dateFormat';
import { useLocalDate } from '@/store/useLocalDate';

import JobPagination from './JobPagination';

const AgentCallList = () => {
  const [searchParams] = useSearchParams();
  const name = searchParams.get('name') || '';
  const startDate = searchParams.get('startDate') || '';
  const endDate = searchParams.get('endDate') || '';
  const page = searchParams.get('page') || '1';

  const { locale, place } = useLocalDate();

  const {
    data: { logs, pages },
  } = useGetJobList({
    user_name: name,
    start_date: startDate,
    end_date: endDate,
    page: page,
    size: '4',
  });

  const { push } = useInternalRouter();
  const location = useLocation();

  const handleLogClick = (logId: string) => {
    const searchParams = new URLSearchParams(location.search);
    searchParams.set('logId', logId);
    push(`?${searchParams.toString()}`);
  };

  return (
    <div className='flex h-full w-full flex-col justify-between gap-5'>
      <section className='grid h-full w-full grid-cols-1 grid-rows-4 gap-2'>
        {logs.map(log => (
          <Card
            key={log.log_id}
            onClick={() => handleLogClick(log.log_id)}
            className='group w-full flex-1 cursor-pointer transition-all'
          >
            <CardHeader className=''>
              <div className='flex items-center justify-between'>
                <CardTitle className='text-md font-bold text-slate-800'>
                  {log.agent_name}
                </CardTitle>
                <Badge variant='outline'>
                  {formatDateTime(log.created_at, locale, place)}
                </Badge>
              </div>
              <CardDescription className='line-clamp-2 text-xs text-slate-600'>
                {log.log_detail}
              </CardDescription>
            </CardHeader>
            <CardContent className='flex items-center gap-2 pt-0'>
              <div className='flex items-center gap-2'>
                <User className='h-4 w-4' />
                <span className='text-xs font-medium text-slate-700'>
                  {log.user_name}
                </span>
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

      <JobPagination pages={pages} />
    </div>
  );
};

export default AgentCallList;
