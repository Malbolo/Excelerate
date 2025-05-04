import { useEffect, useRef } from 'react';

const useClickOutsideRef = <T extends HTMLElement>(
  handleClickOutsideRef: () => void,
) => {
  const ref = useRef<T>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        handleClickOutsideRef();
      }
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [ref, handleClickOutsideRef]);

  return ref;
};

export default useClickOutsideRef;
