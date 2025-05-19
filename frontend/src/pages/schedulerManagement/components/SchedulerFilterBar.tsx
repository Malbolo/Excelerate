import { useCallback, useState } from 'react';

// useEffect 제거
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

  return {
    searchQuery: query,
    searchType: type,
    frequency: searchParams.get('frequency') || FREQUENCIES[0].value,
    status: searchParams.get('status') || STATUSES[0].value,
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

      currentRawParams.forEach((value, key) => {
        if (key === 'page') return;
        if (!(key in newParamValues) && value && value !== 'all') {
          nextParams.set(key, value);
        }
      });

      for (const key in newParamValues) {
        const value = newParamValues[key];
        if (value === undefined || value === '' || value === 'all') {
          nextParams.delete(key);
        } else {
          nextParams.set(key, value as string);
        }
      }

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

  const handleClearAllFilters = () => {
    const defaultState = getInitialFilterState(new URLSearchParams()); // 깨끗한 초기 상태
    setCurrentSearchQuery(defaultState.searchQuery);
    setCurrentSearchType(defaultState.searchType);
    setCurrentFrequency(defaultState.frequency);
    setCurrentStatus(defaultState.status);
    setCurrentSize(defaultState.size);

    updateUrlParams(
      {
        title: undefined, // title 파라미터 제거
        owner: undefined, // owner 파라미터 제거
        frequency: FREQUENCIES[0].value, // 'all' (기본값, updateUrlParams에서 처리)
        status: STATUSES[0].value, // 'all' (기본값, updateUrlParams에서 처리)
        size: SIZES[0], // 기본 사이즈 (updateUrlParams에서 처리)
      },
      true,
    );
  };

  const currentSearchTypeLabel = SEARCH_TYPES.find(st => st.value === currentSearchType)?.label || 'Keyword';

  return (
    <div className='flex w-full flex-wrap items-center gap-2 md:gap-3'>
      <div className='xs:w-auto w-full flex-shrink-0 sm:w-auto md:w-[130px]'>
        <label htmlFor='st-type' className='sr-only'>
          Search Type
        </label>
        <Select value={currentSearchType} onValueChange={handleSearchTypeChange}>
          <SelectTrigger id='st-type'>
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

      <div className='xs:w-auto xs:order-none order-first w-full flex-grow sm:order-none sm:w-auto'>
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

      <div className='xs:w-auto w-full flex-shrink-0 sm:w-auto'>
        <Button onClick={handleSearchSubmit} variant='default' className='w-full'>
          Search
        </Button>
      </div>

      <div className='mx-1 hidden h-6 border-l border-slate-300 md:block'></div>

      <div className='xs:w-auto w-full flex-shrink-0 sm:w-auto md:w-[160px]'>
        <label htmlFor='st-frequency' className='sr-only'>
          Frequency
        </label>
        <Select value={currentFrequency} onValueChange={handleFrequencyChange}>
          <SelectTrigger id='st-frequency'>
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

      <div className='xs:w-auto w-full flex-shrink-0 sm:w-auto md:w-[140px]'>
        <label htmlFor='st-status' className='sr-only'>
          Status
        </label>
        <Select value={currentStatus} onValueChange={handleStatusChange}>
          <SelectTrigger id='st-status'>
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

      <div className='xs:w-auto w-full flex-shrink-0 sm:w-auto md:w-[140px]'>
        <label htmlFor='st-size' className='sr-only'>
          Items per page
        </label>
        <Select value={currentSize} onValueChange={handleSizeChange}>
          <SelectTrigger id='st-size'>
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

      <div className='xs:w-auto w-full flex-shrink-0 sm:w-auto'>
        <Button variant='ghost' onClick={handleClearAllFilters} className='w-full text-slate-600 hover:text-slate-800'>
          Clear All
        </Button>
      </div>
    </div>
  );
};

export default SchedulerFilterBar;
