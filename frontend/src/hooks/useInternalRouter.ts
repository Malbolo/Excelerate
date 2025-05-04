import { useMemo } from 'react';

import { useNavigate } from 'react-router-dom';

const useInternalRouter = () => {
  const navigate = useNavigate();

  return useMemo(() => {
    return {
      goBack() {
        navigate(-1);
      },
      push(path: RoutePath, data?: any) {
        navigate(path, { state: data });
      },
      replace(path: RoutePath) {
        navigate(path, { replace: true });
      },
    };
  }, [navigate]);
};

export default useInternalRouter;

type RoutePath = `/${string}`;
