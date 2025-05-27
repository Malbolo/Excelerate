import usePagination from '@/components/Pagination/usePagination';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';

const CustomPagination = ({ totalPages }: { totalPages: number }) => {
  const { curPage, handlePageChange, pageNumbers } = usePagination(totalPages);

  return (
    <Pagination>
      <PaginationContent>
        {curPage !== 1 && (
          <PaginationItem>
            <PaginationPrevious onClick={() => handlePageChange(Math.max(1, curPage - 1))} />
          </PaginationItem>
        )}
        {pageNumbers.map(pageNum => (
          <PaginationItem key={pageNum}>
            <PaginationLink isActive={curPage === pageNum} onClick={() => handlePageChange(pageNum)}>
              {pageNum}
            </PaginationLink>
          </PaginationItem>
        ))}
        <PaginationItem>
          <PaginationNext
            onClick={() => handlePageChange(Math.min(totalPages, curPage + 1))}
            aria-disabled={curPage === totalPages}
          />
        </PaginationItem>
      </PaginationContent>
    </Pagination>
  );
};

export default CustomPagination;
