import { ChangeEvent, KeyboardEvent, useEffect, useState } from 'react';

import { SearchIcon } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const JobSearchInput = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Initialize state from URL params or defaults
  // 1 & 2. Department와 Type의 초기값을 ''로 설정하여 placeholder가 보이도록 함
  const initialDep = searchParams.get('dep') || ''; // ''로 설정하여 placeholder 표시 유도
  const initialType = searchParams.get('type') || ''; // ''로 설정하여 placeholder 표시 유도

  // 4. searchField는 URL에서 직접 읽지 않고, title 또는 name 파라미터 존재 여부로 유추
  let determinedInitialSearchField = 'title'; // 기본값
  let determinedInitialSearchQuery = '';

  if (searchParams.has('title')) {
    determinedInitialSearchField = 'title';
    determinedInitialSearchQuery = searchParams.get('title') || '';
  } else if (searchParams.has('name')) {
    // 'user' 검색 필드에 해당하는 URL 파라미터가 'name'이라고 가정
    determinedInitialSearchField = 'user';
    determinedInitialSearchQuery = searchParams.get('name') || '';
  }
  // 만약 'searchField' 파라미터가 레거시로 여전히 존재할 수 있다면, 그 값을 우선할 수도 있습니다.
  // 하지만 요청사항은 searchField를 URL 파라미터로 사용하지 않는 것이므로 위 로직을 따릅니다.

  const [dep, setDep] = useState<string>(initialDep);
  const [type, setType] = useState<string>(initialType);
  const [searchField, setSearchField] = useState<string>(
    determinedInitialSearchField,
  );
  const [searchValue, setSearchValue] = useState<string>(
    determinedInitialSearchQuery,
  );

  useEffect(() => {
    const currentDep = searchParams.get('dep') || '';
    const currentType = searchParams.get('type') || '';

    let currentInferredSearchField = 'title';
    let currentInferredSearchValue = '';

    if (searchParams.has('title')) {
      currentInferredSearchField = 'title';
      currentInferredSearchValue = searchParams.get('title') || '';
    } else if (searchParams.has('name')) {
      currentInferredSearchField = 'user';
      currentInferredSearchValue = searchParams.get('name') || '';
    }

    if (dep !== currentDep) setDep(currentDep);
    if (type !== currentType) setType(currentType);
    if (searchField !== currentInferredSearchField)
      setSearchField(currentInferredSearchField);
    if (searchValue !== currentInferredSearchValue)
      setSearchValue(currentInferredSearchValue);
  }, [searchParams]);

  const handleSearch = () => {
    setSearchParams(
      prev => {
        const newParams = new URLSearchParams(prev.toString());
        newParams.delete('title');
        newParams.delete('name');
        newParams.delete('keyword');

        newParams.delete('searchField');

        const trimmedSearchValue = searchValue.trim();
        if (trimmedSearchValue) {
          if (searchField === 'user') {
            newParams.set('name', trimmedSearchValue);
          } else {
            newParams.set('title', trimmedSearchValue);
          }
        }

        if (dep) {
          newParams.set('dep', dep);
        } else {
          newParams.delete('dep');
        }

        if (type) {
          newParams.set('type', type);
        } else {
          newParams.delete('type');
        }

        newParams.set('page', '1');
        return newParams;
      },
      { replace: true },
    );
  };

  const handleDepChange = (value: string) => {
    setDep(value);
  };

  const handleTypeChange = (value: string) => {
    setType(value);
  };

  const handleSearchFieldChange = (value: string) => {
    setSearchField(value);
    setSearchValue('');
  };

  const handleSearchValueChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const executeSearch = () => {
    handleSearch();
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      executeSearch();
    }
  };

  return (
    <div className='bg-background flex flex-wrap items-center gap-2 p-2.5'>
      <Select value={dep} onValueChange={handleDepChange}>
        <SelectTrigger className='h-9 w-auto min-w-[130px] text-xs focus:ring-0 focus:ring-offset-0 sm:text-sm'>
          <SelectValue placeholder='Department' />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='developer' className='text-xs sm:text-sm'>
            Developer
          </SelectItem>
          <SelectItem value='manager' className='text-xs sm:text-sm'>
            Manager
          </SelectItem>
          <SelectItem value='super' className='text-xs sm:text-sm'>
            Super
          </SelectItem>
          <SelectItem value='all' className='text-xs sm:text-sm'>
            All Departments
          </SelectItem>
        </SelectContent>
      </Select>

      <Select value={type} onValueChange={handleTypeChange}>
        <SelectTrigger className='h-9 w-auto min-w-[120px] text-xs focus:ring-0 focus:ring-offset-0 sm:text-sm'>
          <SelectValue placeholder='Job Type' />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='create' className='text-xs sm:text-sm'>
            Create
          </SelectItem>
          <SelectItem value='delete' className='text-xs sm:text-sm'>
            Delete
          </SelectItem>
          <SelectItem value='update' className='text-xs sm:text-sm'>
            Update
          </SelectItem>
          <SelectItem value='read' className='text-xs sm:text-sm'>
            Read
          </SelectItem>
          <SelectItem value='all' className='text-xs sm:text-sm'>
            All Types
          </SelectItem>
        </SelectContent>
      </Select>

      <Select value={searchField} onValueChange={handleSearchFieldChange}>
        <SelectTrigger className='h-9 w-auto min-w-[110px] text-xs focus:ring-0 focus:ring-offset-0 sm:text-sm'>
          <SelectValue placeholder='Search By' />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value='title' className='text-xs sm:text-sm'>
            Title
          </SelectItem>
          <SelectItem value='user' className='text-xs sm:text-sm'>
            User
          </SelectItem>
        </SelectContent>
      </Select>

      <div className='flex min-w-[200px] flex-grow items-center'>
        <Input
          type='text'
          placeholder={
            searchField === 'title'
              ? 'Search by title...'
              : 'Search by user name...'
          }
          value={searchValue}
          onChange={handleSearchValueChange}
          onKeyDown={handleKeyDown}
          className='h-9 flex-grow rounded-r-none border-r-0 text-xs focus:ring-0 focus:ring-offset-0 sm:text-sm'
        />
        <Button
          onClick={executeSearch}
          size='sm'
          className='h-9 rounded-l-none px-3 text-xs sm:text-sm'
          aria-label='Search'
        >
          <SearchIcon className='h-4 w-4' />
        </Button>
      </div>
    </div>
  );
};

export default JobSearchInput;
