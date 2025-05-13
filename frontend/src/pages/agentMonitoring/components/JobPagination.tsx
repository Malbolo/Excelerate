import { useSearchParams } from 'react-router-dom';

import { useGetJobList } from '@/apis/agentMonitoring';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import useInternalRouter from '@/hooks/useInternalRouter';
import usePagination from '@/hooks/usePagination';
import { formatDateTime } from '@/pages/schedulerManagement/utils/formatInterval';

// 다른 컴포넌트에서 사용하는 페이지네이션과 통일해서 하나의 로직으로 합쳐야함
// 페이지네이션 컴포넌트는 page의 쿼리파라미터를 받아서 페이지네이션을 관리하는 로직만을 가지고 있어야함
const JobPagination = () => {
  const [searchParams] = useSearchParams();
  const name = searchParams.get('name') || '';
  const startDate = searchParams.get('startDate') || '';
  const endDate = searchParams.get('endDate') || '';
  const page = searchParams.get('page') || '1';

  const {
    data: { logs, pages },
  } = useGetJobList({
    user_name: name,
    start_date: startDate,
    end_date: endDate,
    page: page,
    size: '4',
  });

  const { curPage, handlePageChange, pageNumbers } = usePagination(pages);

  const { push } = useInternalRouter();

  return (
    <div className='flex w-full grow flex-col justify-between'>
      <section className='grid w-full grid-cols-1 gap-4'>
        {logs.map(log => (
          <Card
            key={log.log_id}
            onClick={() => push(`/agent-monitoring/job/${log.log_id}`)}
            className='w-full cursor-pointer p-5'
          >
            <CardHeader>
              <CardTitle>{log.agent_name}</CardTitle>
              <CardDescription>{log.log_detail}</CardDescription>
            </CardHeader>
            <CardContent className='flex w-full justify-between'>
              <p>{log.user_name}</p>
              <p>{formatDateTime(log.created_at)}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => handlePageChange(Math.max(1, curPage - 1))}
              aria-disabled={curPage === 1}
            />
          </PaginationItem>
          {pageNumbers.map(pageNum => (
            <PaginationItem key={pageNum}>
              <PaginationLink
                isActive={curPage === pageNum}
                onClick={() => handlePageChange(pageNum)}
              >
                {pageNum}
              </PaginationLink>
            </PaginationItem>
          ))}
          <PaginationItem>
            <PaginationNext
              onClick={() => handlePageChange(Math.min(pages, curPage + 1))}
              aria-disabled={curPage === pages}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

export default JobPagination;
