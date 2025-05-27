import { useCallback, useState } from 'react';

import { useSearchParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export const SIZES = ['10', '50', '100'];
export const SEARCH_TYPES = [
  { value: 'title', label: 'Title' },
  { value: 'owner', label: 'Owner' },
];
export const FREQUENCIES = [
  { value: 'all', label: 'All Frequencies' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
];
export const STATUSES = [
  { value: 'active', label: 'Active' },
  { value: 'paused', label: 'Paused' },
  { value: 'all', label: 'All Statuses' },
];

const getInitialFilterState = (searchParams: URLSearchParams) => {
  let type = SEARCH_TYPES[0].value;
  let query = '';

  const ownerParam = searchParams.get('owner');
  const titleParam = searchParams.get('title');

  if (ownerParam !== null) {
    type = 'owner';
    query = ownerParam;
  } else if (titleParam !== null) {
    type = 'title';
    query = titleParam;
  }

  // 'status'의 기본값은 'active'이지만, 'all'이 URL에 명시적으로 있으면 'all'을 사용합니다.
  const statusParam = searchParams.get('status');
  const initialStatus = statusParam === 'all' ? 'all' : statusParam || STATUSES[0].value;

  return {
    searchQuery: query,
    searchType: type,
    frequency: searchParams.get('frequency') || FREQUENCIES[0].value,
    status: initialStatus,
    size: searchParams.get('size') || SIZES[0],
  };
};

const SchedulerFilterBar = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const initialFilters = getInitialFilterState(searchParams);
  const [currentSearchQuery, setCurrentSearchQuery] = useState(initialFilters.searchQuery);
  const [currentSearchType, setCurrentSearchType] = useState(initialFilters.searchType);
  const [currentFrequency, setCurrentFrequency] = useState(initialFilters.frequency);
  const [currentStatus, setCurrentStatus] = useState(initialFilters.status);
  const [currentSize, setCurrentSize] = useState(initialFilters.size);

  const updateUrlParams = useCallback(
    (newParamValues: Record<string, string | undefined>, resetPage = true) => {
      const currentRawParams = new URLSearchParams(searchParams);
      const nextParams = new URLSearchParams();

      // 기존 파라미터 중 새로 설정되지 않고 'all'이 아닌 값들을 유지
      currentRawParams.forEach((value, key) => {
        if (key === 'page') return;
        if (!(key in newParamValues) && value && value !== 'all') {
          // 'status'가 'all'인 경우는 유지해야 하므로, 아래 루프에서 처리하도록 여기서 제외
          if (key !== 'status' || value !== 'all') {
            nextParams.set(key, value);
          }
        }
      });

      // 새로운 파라미터 값 적용
      for (const key in newParamValues) {
        const value = newParamValues[key];

        if (value === undefined || value === '') {
          nextParams.delete(key);
        } else if (value === 'all') {
          // 'frequency'가 'all'이면 삭제 (빈 문자열 처리)
          if (key === 'frequency') {
            nextParams.delete(key);
          }
          // 'status'가 'all'이면 'all'로 설정
          else if (key === 'status') {
            nextParams.set(key, value as string);
          }
          // 그 외의 'all'은 삭제
          else {
            nextParams.delete(key);
          }
        } else {
          nextParams.set(key, value as string);
        }
      }

      // 페이지 파라미터 처리
      const existingPage = currentRawParams.get('page');
      const hasOtherFilters = Array.from(nextParams.keys()).some(k => k !== 'page');

      if (resetPage) {
        if (hasOtherFilters) {
          nextParams.set('page', '1');
        } else {
          nextParams.delete('page');
        }
      } else if (existingPage) {
        if (
          hasOtherFilters ||
          (existingPage !== '1' && Array.from(nextParams.keys()).filter(k => k !== 'page').length === 0)
        ) {
          nextParams.set('page', existingPage);
        } else {
          nextParams.delete('page');
        }
      } else {
        if (hasOtherFilters) {
          nextParams.set('page', '1');
        } else {
          nextParams.delete('page');
        }
      }

      // 최종 URL 설정
      const keys = Array.from(nextParams.keys());
      if (keys.length === 0) {
        setSearchParams({}, { replace: true });
      } else if (keys.length === 1 && keys[0] === 'page' && nextParams.get('page') === '1') {
        setSearchParams({}, { replace: true });
      } else {
        setSearchParams(nextParams, { replace: true });
      }
    },
    [searchParams, setSearchParams],
  );

  const handleSearchTypeChange = (newSearchType: string) => {
    const oldSearchType = currentSearchType;
    setCurrentSearchType(newSearchType);
    setCurrentSearchQuery('');
    updateUrlParams({ [oldSearchType]: undefined }, true);
  };

  const handleSearchInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setCurrentSearchQuery(event.target.value);
  };

  const handleSearchSubmit = () => {
    const paramsToUpdate: Record<string, string | undefined> = {
      title: undefined,
      owner: undefined,
    };
    if (currentSearchQuery.trim()) {
      paramsToUpdate[currentSearchType] = currentSearchQuery.trim();
    }
    updateUrlParams(paramsToUpdate, true);
  };

  const handleFrequencyChange = (newFrequency: string) => {
    setCurrentFrequency(newFrequency);
    updateUrlParams({ frequency: newFrequency }, true);
  };

  const handleStatusChange = (newStatus: string) => {
    setCurrentStatus(newStatus);
    updateUrlParams({ status: newStatus }, true);
  };

  const handleSizeChange = (newSize: string) => {
    setCurrentSize(newSize);
    updateUrlParams({ size: newSize }, true);
  };

  // handleClearAllFilters 수정: status를 'all'로 설정하고, frequency도 'all'로 설정하여
  // updateUrlParams에서 각각 'all'과 빈 문자열로 처리되도록 함
  const handleClearAllFilters = () => {
    setCurrentSearchQuery('');
    setCurrentSearchType(SEARCH_TYPES[0].value);
    setCurrentFrequency(FREQUENCIES[0].value); // 'all'
    setCurrentStatus('all'); // 'all'로 설정
    setCurrentSize(SIZES[0]);

    updateUrlParams(
      {
        title: undefined,
        owner: undefined,
        frequency: 'all', // 'all' -> updateUrlParams에서 삭제됨
        status: 'all', // 'all' -> updateUrlParams에서 'all'로 설정됨
        size: SIZES[0], // 기본 사이즈 (삭제되지 않음)
      },
      true,
    );
  };

  const currentSearchTypeLabel = SEARCH_TYPES.find(st => st.value === currentSearchType)?.label || 'Keyword';

  return (
    <div className='flex w-full flex-wrap items-center gap-2 md:gap-3'>
      {/* Search Type Select */}
      <div className='flex-1'>
        <label htmlFor='st-type' className='sr-only'>
          Search Type
        </label>
        <Select value={currentSearchType} onValueChange={handleSearchTypeChange}>
          <SelectTrigger id='st-type' className='w-full'>
            <SelectValue placeholder='Type' />
          </SelectTrigger>
          <SelectContent>
            {SEARCH_TYPES.map(st => (
              <SelectItem key={st.value} value={st.value}>
                {st.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Search Input */}
      <div className='flex-2'>
        <label htmlFor='st-query' className='sr-only'>
          Search Query
        </label>
        <Input
          id='st-query'
          type='text'
          placeholder={`Enter ${currentSearchTypeLabel}...`}
          value={currentSearchQuery}
          onChange={handleSearchInputChange}
          onKeyDown={e => e.key === 'Enter' && handleSearchSubmit()}
          className='w-full'
        />
      </div>

      {/* Search Button */}
      <div className='xs:w-auto w-full flex-shrink-0 sm:w-auto'>
        <Button onClick={handleSearchSubmit} variant='default' className='w-full'>
          Search
        </Button>
      </div>

      <div className='mx-1 hidden h-6 border-l md:block'></div>

      {/* Frequency Select */}
      <div className='flex-1'>
        <label htmlFor='st-frequency' className='sr-only'>
          Frequency
        </label>
        <Select value={currentFrequency} onValueChange={handleFrequencyChange}>
          <SelectTrigger id='st-frequency' className='w-full'>
            <SelectValue placeholder='Frequency' />
          </SelectTrigger>
          <SelectContent>
            {FREQUENCIES.map(f => (
              <SelectItem key={f.value} value={f.value}>
                {f.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Status Select */}
      <div className='flex-1'>
        <label htmlFor='st-status' className='sr-only'>
          Status
        </label>
        <Select value={currentStatus} onValueChange={handleStatusChange}>
          <SelectTrigger id='st-status' className='w-full'>
            <SelectValue placeholder='Status' />
          </SelectTrigger>
          <SelectContent>
            {STATUSES.map(s => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Size Select */}
      <div className='flex-1'>
        <label htmlFor='st-size' className='sr-only'>
          Items per page
        </label>
        <Select value={currentSize} onValueChange={handleSizeChange}>
          <SelectTrigger id='st-size' className='w-full'>
            <SelectValue placeholder='Items/page' />
          </SelectTrigger>
          <SelectContent>
            {SIZES.map(s => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Clear All Button */}
      <div className='xs:w-auto w-full flex-shrink-0 sm:w-auto'>
        <Button variant='outline' onClick={handleClearAllFilters}>
          Clear All
        </Button>
      </div>
    </div>
  );
};

export default SchedulerFilterBar;
