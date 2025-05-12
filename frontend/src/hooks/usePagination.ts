import { useEffect, useState } from 'react';

import { useLocation } from 'react-router-dom';

import useInternalRouter from '@/hooks/useInternalRouter';

const usePagination = (totalPages: number) => {
  const [curPage, setCurPage] = useState(1);
  const pageRange = 10; // 한 번에 보여줄 페이지 수

  const { push, replace } = useInternalRouter();

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const page = Number(params.get('page'));

  // 현재 페이지 범위 계산
  const startPage = Math.floor((curPage - 1) / pageRange) * pageRange + 1;
  const endPage = Math.min(startPage + pageRange - 1, totalPages);

  // 페이지 번호 배열 생성
  const pageNumbers = Array.from(
    { length: endPage - startPage + 1 },
    (_, i) => startPage + i,
  );

  useEffect(() => {
    if (!page || isNaN(page) || page < 1 || page > totalPages) {
      params.set('page', '1');
      replace({ search: params.toString() });
      return;
    }

    setCurPage(page);
  }, [page]);

  const handlePageChange = (page: number) => {
    params.set('page', String(page));
    push({ search: params.toString() });
  };

  return {
    curPage,
    handlePageChange,
    pageNumbers,
    startPage,
    endPage,
    pageRange,
  };
};

export default usePagination;
