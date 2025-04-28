import { ChangeEvent, KeyboardEvent, useEffect, useState } from 'react';

import { SearchIcon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface JobSearchInputProps {
  initialKeyword: string;
  onSearch: (keyword: string) => void;
}

// todo: tanstack query로 invalidate 처리 예정
// 쿼리파라미터만 변경하여 쿼리 재호출 예정
const JobSearchInput = ({ initialKeyword, onSearch }: JobSearchInputProps) => {
  const [localKeyword, setLocalKeyword] = useState(initialKeyword);

  useEffect(() => {
    setLocalKeyword(initialKeyword);
  }, [initialKeyword]);

  const handleKeywordChange = (event: ChangeEvent<HTMLInputElement>) => {
    setLocalKeyword(event.target.value);
  };

  const executeSearch = () => {
    onSearch(localKeyword);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      executeSearch();
    }
  };

  return (
    <div className='mb-4 flex gap-2'>
      <Input
        type='text'
        placeholder='JOB 제목 또는 설명 검색...'
        value={localKeyword}
        onChange={handleKeywordChange}
        onKeyDown={handleKeyDown}
        className='flex-grow'
      />
      <Button onClick={executeSearch}>
        <SearchIcon className='mr-2 h-4 w-4' /> 검색
      </Button>
    </div>
  );
};

export default JobSearchInput;
