import { useEffect, useState } from 'react';

import { useLocation } from 'react-router-dom';

import useInternalRouter from '@/hooks/useInternalRouter';

const PAGE_SIZE = 4;

const usePagination = <T>(totalItems: T[]) => {
  const [curPage, setCurPage] = useState(1);

  const { push, replace } = useInternalRouter();

  const location = useLocation();
  const params = new URLSearchParams(location.search);
  const page = Number(params.get('page'));

  const totalPages = Math.ceil(totalItems.length / PAGE_SIZE);
  const pagedItems = totalItems.slice(
    (curPage - 1) * PAGE_SIZE,
    curPage * PAGE_SIZE,
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

  return { curPage, totalPages, pagedItems, handlePageChange };
};

export default usePagination;
