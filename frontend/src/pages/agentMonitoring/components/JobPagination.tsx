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
import { MJobTable } from '@/mocks/datas/dataframe';
import { Job } from '@/types/scheduler';

const JobPagination: React.FC = () => {
  // TODO: 백엔드 서버 API 연동 시 사용
  // const [searchParams] = useSearchParams();
  // const uid = searchParams.get('uid') || '';

  // const { data: jobList } = useGetJobList({
  //   uid,
  //   page: '1',
  //   size: String(PAGE_SIZE),
  // });

  const { curPage, totalPages, pagedItems, handlePageChange } =
    usePagination<Job>(MJobTable);

  const { push } = useInternalRouter();

  return (
    <>
      <section className='flex flex-1 flex-col gap-4'>
        {pagedItems.map(job => (
          <Card
            key={job.jobId}
            onClick={() => push(`/agent-monitoring/job/${job.jobId}`)}
            className='cursor-pointer p-5'
          >
            <CardHeader>
              <CardTitle>{job.title}</CardTitle>
              <CardDescription>{job.description}</CardDescription>
            </CardHeader>
            <CardContent className='flex w-full justify-between'>
              <p>{job.userName}</p>
              <p>{job.createdAt}</p>
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
          {Array.from({ length: totalPages }).map((_, index) => (
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
              onClick={() =>
                handlePageChange(Math.min(totalPages, curPage + 1))
              }
              aria-disabled={curPage === totalPages}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </>
  );
};

export default JobPagination;
