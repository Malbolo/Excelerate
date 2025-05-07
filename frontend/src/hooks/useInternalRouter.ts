import { useMemo } from 'react';

import { To, useNavigate } from 'react-router-dom';

const useInternalRouter = () => {
  const navigate = useNavigate();

  return useMemo(() => {
    return {
      goBack() {
        navigate(-1);
      },
      push(path: RoutePath | To) {
        navigate(path);
      },
      replace(path: RoutePath | To) {
        navigate(path, { replace: true });
      },
    };
  }, [navigate]);
};

export default useInternalRouter;

type RoutePath = `/${string}`;
