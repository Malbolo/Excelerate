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

const JobPagination: React.FC = () => {
  const [searchParams] = useSearchParams();
  const name = searchParams.get('name') || '';
  const startDate = searchParams.get('startDate') || '';
  const endDate = searchParams.get('endDate') || '';
  const page = searchParams.get('page') || '1';

  const {
    data: { jobs, total },
  } = useGetJobList({
    name,
    startdate: startDate,
    enddate: endDate,
    page: page,
    size: '4',
  });

  const { curPage, handlePageChange } = usePagination(total);

  const { push } = useInternalRouter();

  return (
    <>
      <section className='flex flex-1 flex-col gap-4'>
        {jobs.map(job => (
          <Card
            key={job.id}
            onClick={() => push(`/agent-monitoring/job/${job.id}`)}
            className='flex-1 cursor-pointer p-5'
          >
            <CardHeader>
              <CardTitle>{job.title}</CardTitle>
              <CardDescription>{job.description}</CardDescription>
            </CardHeader>
            <CardContent className='flex w-full justify-between'>
              <p>{job.user_name}</p>
              <p>{job.created_at}</p>
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
          {Array.from({ length: total }).map((_, index) => (
            <PaginationItem key={index}>
              <PaginationLink
                isActive={curPage === index + 1}
                onClick={() => handlePageChange(index + 1)}
              >
                {index + 1}
              </PaginationLink>
            </PaginationItem>
          ))}
          <PaginationItem>
            <PaginationNext
              onClick={() => handlePageChange(Math.min(total, curPage + 1))}
              aria-disabled={curPage === total}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </>
  );
};

export default JobPagination;
