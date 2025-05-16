import { useEffect, useState } from 'react';

import { useSearchParams } from 'react-router-dom';

import useInternalRouter from '@/hooks/useInternalRouter';

const PAGE_RANGE = 5;

const usePagination = (totalPages: number) => {
  const [curPage, setCurPage] = useState(1);
  const [searchParams, setSearchParams] = useSearchParams();

  const { push } = useInternalRouter();

  const page = Number(searchParams.get('page'));

  // 현재 페이지 범위 계산
  const startPage = Math.floor((curPage - 1) / PAGE_RANGE) * PAGE_RANGE + 1;
  const endPage = Math.min(startPage + PAGE_RANGE - 1, totalPages);

  // 페이지 번호 배열 생성
  const pageNumbers = Array.from({ length: endPage - startPage + 1 }, (_, i) => startPage + i);

  useEffect(() => {
    if (!page || isNaN(page) || page < 1 || page > totalPages) {
      searchParams.set('page', '1');
      setSearchParams(searchParams);
      return;
    }

    setCurPage(page);
  }, [page]);

  const handlePageChange = (page: number) => {
    searchParams.set('page', String(page));
    push({ search: searchParams.toString() });
  };

  return { curPage, handlePageChange, pageNumbers };
};

export default usePagination;
