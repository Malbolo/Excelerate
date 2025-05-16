import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
import usePagination from '@/hooks/usePagination';

// 다른 컴포넌트에서 사용하는 페이지네이션과 통일해서 하나의 로직으로 합쳐야함
// 페이지네이션 컴포넌트는 page의 쿼리파라미터를 받아서 페이지네이션을 관리하는 로직만을 가지고 있어야함
const JobPagination = ({ pages }: { pages: number }) => {
  const { curPage, handlePageChange, pageNumbers } = usePagination(pages);

  return (
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
            <PaginationLink isActive={curPage === pageNum} onClick={() => handlePageChange(pageNum)}>
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
  );
};

export default JobPagination;
