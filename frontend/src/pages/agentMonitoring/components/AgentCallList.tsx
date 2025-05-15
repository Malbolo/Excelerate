import { useSearchParams } from 'react-router-dom';

import { useGetJobList } from '@/apis/agentMonitoring';
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

  return (
    <div className='flex h-full w-full flex-col justify-between'>
      <section className='grid w-full grid-cols-1'>
        {logs.map(log => (
          <Card
            key={log.log_id}
            onClick={() => push(`?logId=${log.log_id}`)}
            className='w-full cursor-pointer p-5'
          >
            <CardHeader>
              <CardTitle>{log.agent_name}</CardTitle>
              <CardDescription>{log.log_detail}</CardDescription>
            </CardHeader>
            <CardContent className='flex w-full justify-between'>
              <p>{log.user_name}</p>
              <p>{formatDateTime(log.created_at, locale, place)}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <JobPagination pages={pages} />
    </div>
  );
};

export default AgentCallList;
