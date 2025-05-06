import { useMemo } from 'react';

import { To, useNavigate } from 'react-router-dom';

const useInternalRouter = () => {
  const navigate = useNavigate();

  return useMemo(() => {
    return {
      goBack() {
        navigate(-1);
      },
      push(path: RoutePath | To, data?: any) {
        if (typeof path === 'object') {
          navigate(path);
        } else {
          navigate(path, { state: data });
        }
      },
      replace(path: RoutePath | To) {
        if (typeof path === 'object') {
          navigate(path, { replace: true });
        } else {
          navigate(path, { replace: true });
        }
      },
    };
  }, [navigate]);
};

export default useInternalRouter;

type RoutePath = `/${string}`;
