import { useCallback } from 'react';

import { useSearchParams } from 'react-router-dom';

import { useGetJobList } from '@/apis/jobManagement';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import { ITEMS_PER_PAGE } from '@/pages/jobManagement';

const JobPagination = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const keyword = searchParams.get('keyword') || '';
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

  const { data: jobList } = useGetJobList(currentPage, ITEMS_PER_PAGE, keyword);
  const { total } = jobList;

  const handlePageChange = useCallback(
    (page: number) => {
      if (page >= 1 && page <= total) {
        setSearchParams(
          prev => {
            prev.set('page', page.toString());
            return prev;
          },
          { replace: true },
        );
      }
    },
    [total, setSearchParams],
  );

  // Delete : 더미데이터를 위해 사용, 추후에는 실제 페이지 번호 사용 필요
  // Info : Response로 Spring의 Pageable 타입을 사용하여 페이지 번호를 받아오므로, 페이지 번호를 변경할 때 주의 필요
  const renderPageNumbers = () => {
    const pages = [];
    for (let i = 1; i <= total; i++) {
      pages.push(
        <PaginationItem key={i}>
          <PaginationLink
            href='#'
            isActive={i === currentPage}
            onClick={e => {
              e.preventDefault();
              handlePageChange(i);
            }}
          >
            {i}
          </PaginationLink>
        </PaginationItem>,
      );
    }
    return pages;
  };

  return (
    <div className='mt-4 flex justify-center'>
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              href='#'
              onClick={e => {
                e.preventDefault();
                handlePageChange(currentPage - 1);
              }}
              className={
                currentPage === 1 ? 'pointer-events-none opacity-50' : undefined
              }
            />
          </PaginationItem>
          {renderPageNumbers()}
          <PaginationItem>
            <PaginationNext
              href='#'
              onClick={e => {
                e.preventDefault();
                handlePageChange(currentPage + 1);
              }}
              className={
                currentPage === total
                  ? 'pointer-events-none opacity-50'
                  : undefined
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

export default JobPagination;
