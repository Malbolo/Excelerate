import { ChangeEvent, KeyboardEvent, useState } from 'react';

import { SearchIcon } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

// todo: tanstack query로 invalidate 처리 예정
// 쿼리파라미터만 변경하여 쿼리 재호출 예정
const JobSearchInput = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const keyword = searchParams.get('keyword') || '';
  const [localKeyword, setLocalKeyword] = useState(keyword);

  const handleSearch = (newKeyword: string) => {
    setSearchParams(
      prev => {
        prev.set('keyword', newKeyword);
        prev.set('page', '1');
        return prev;
      },
      { replace: true },
    );
  };

  const handleKeywordChange = (event: ChangeEvent<HTMLInputElement>) => {
    setLocalKeyword(event.target.value);
  };

  const executeSearch = () => {
    handleSearch(localKeyword);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      executeSearch();
    }
  };

  return (
    <div className='flex gap-2 p-4'>
      <Input
        type='text'
        placeholder='Search by job title or description...'
        value={localKeyword}
        onChange={handleKeywordChange}
        onKeyDown={handleKeyDown}
        className='flex-grow'
      />
      <Button onClick={executeSearch}>
        <SearchIcon className='mr-2 h-4 w-4' /> Search
      </Button>
    </div>
  );
};

export default JobSearchInput;
