import React, { useState } from 'react';

import { SearchIcon } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface JobSearchInputProps {
  initialKeyword: string;
  onSearch: (keyword: string) => void;
}

export function JobSearchInput({
  initialKeyword,
  onSearch,
}: JobSearchInputProps) {
  const [localKeyword, setLocalKeyword] = useState(initialKeyword);

  React.useEffect(() => {
    setLocalKeyword(initialKeyword);
  }, [initialKeyword]);

  const handleKeywordChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setLocalKeyword(event.target.value);
  };

  const executeSearch = () => {
    onSearch(localKeyword);
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
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
}
