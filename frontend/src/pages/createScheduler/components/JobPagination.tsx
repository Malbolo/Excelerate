import { useCallback } from 'react';

import { useSearchParams } from 'react-router-dom';

import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';

const JobPagination = ({ total }: { total: number }) => {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentPage = parseInt(searchParams.get('page') || '1', 10);

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

  const renderPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 10;
    const pageNumbersToShow = Math.min(total, maxPagesToShow);

    let startPage: number;
    let endPage: number;

    if (total <= maxPagesToShow) {
      startPage = 1;
      endPage = total;
    } else {
      const maxPagesBeforeCurrentPage = Math.floor((pageNumbersToShow - 1) / 2);
      const maxPagesAfterCurrentPage = Math.ceil((pageNumbersToShow - 1) / 2);

      if (currentPage <= maxPagesBeforeCurrentPage) {
        startPage = 1;
        endPage = pageNumbersToShow;
      } else if (currentPage + maxPagesAfterCurrentPage >= total) {
        startPage = total - pageNumbersToShow + 1;
        endPage = total;
      } else {
        startPage = currentPage - maxPagesBeforeCurrentPage;
        endPage = currentPage + maxPagesAfterCurrentPage;
      }
    }

    if (startPage > 1) {
      pages.push(
        <PaginationItem key={1}>
          <PaginationLink
            href='#'
            onClick={e => {
              e.preventDefault();
              handlePageChange(1);
            }}
          >
            1
          </PaginationLink>
        </PaginationItem>,
      );
      if (startPage > 2) {
        pages.push(
          <PaginationItem key='start-ellipsis'>
            <PaginationEllipsis />
          </PaginationItem>,
        );
      }
    }

    for (let i = startPage; i <= endPage; i++) {
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

    if (endPage < total) {
      if (endPage < total - 1) {
        pages.push(
          <PaginationItem key='end-ellipsis'>
            <PaginationEllipsis />
          </PaginationItem>,
        );
      }
      pages.push(
        <PaginationItem key={total}>
          <PaginationLink
            href='#'
            onClick={e => {
              e.preventDefault();
              handlePageChange(total);
            }}
          >
            {total}
          </PaginationLink>
        </PaginationItem>,
      );
    }

    return pages;
  };

  if (total <= 1) {
    return null;
  }

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
              className={currentPage === 1 ? 'pointer-events-none opacity-50' : undefined}
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
              className={currentPage === total ? 'pointer-events-none opacity-50' : undefined}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

export default JobPagination;
