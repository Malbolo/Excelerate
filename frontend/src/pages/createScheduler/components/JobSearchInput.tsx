import { ChangeEvent, KeyboardEvent, useEffect, useState } from 'react';

import { ChevronsUpDown, SearchIcon } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { JOB_TYPES_CONFIG } from '@/constant/job';

const ALL_TYPES_OPTION = { id: 'all', label: 'All Types' };

const JobSearchInput = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const initialTypesString = searchParams.get('types') || '';
  const initialSelectedTypes = initialTypesString ? initialTypesString.split(',') : [];
  const determinedInitialSearchField = searchParams.has('title') ? 'title' : 'name';
  const determinedInitialSearchQuery = searchParams.get(determinedInitialSearchField) || '';

  const [selectedTypes, setSelectedTypes] = useState(initialSelectedTypes);
  const [searchField, setSearchField] = useState(determinedInitialSearchField);
  const [searchValue, setSearchValue] = useState(determinedInitialSearchQuery);

  useEffect(() => {
    const currentTypesString = searchParams.get('types') || '';
    const currentSelectedTypesFromParams = currentTypesString ? currentTypesString.split(',') : [];

    if (JSON.stringify(selectedTypes.sort()) !== JSON.stringify(currentSelectedTypesFromParams.sort())) {
      setSelectedTypes(currentSelectedTypesFromParams);
    }

    let newSearchFieldState = searchField;
    let newSearchValueState = '';

    if (searchParams.has('title')) {
      newSearchFieldState = 'title';
      newSearchValueState = searchParams.get('title') || '';
    } else if (searchParams.has('name')) {
      newSearchFieldState = 'name';
      newSearchValueState = searchParams.get('name') || '';
    }

    if (searchField !== newSearchFieldState) {
      setSearchField(newSearchFieldState);
    }
    if (searchValue !== newSearchValueState) {
      setSearchValue(newSearchValueState);
    }
  }, [searchParams]);

  const updateSearchParams = (currentUpdatedTypes: string[]) => {
    setSearchParams(
      prev => {
        const newParams = new URLSearchParams(prev.toString());
        newParams.delete('title');
        newParams.delete('name');
        newParams.delete('selectedJob');

        const trimmedSearchValue = searchValue.trim();
        if (trimmedSearchValue) {
          if (searchField === 'name') {
            newParams.set('name', trimmedSearchValue);
          } else {
            newParams.set('title', trimmedSearchValue);
          }
        }

        if (currentUpdatedTypes.length > 0) {
          newParams.set('types', currentUpdatedTypes.join(','));
        } else {
          newParams.delete('types');
        }

        newParams.set('page', '1');
        return newParams;
      },
      { replace: true },
    );
  };

  const handleSelectedTypesChange = (typeId: string, checked: boolean) => {
    let newSelectedTypesArray: string[];

    if (typeId === ALL_TYPES_OPTION.id) {
      newSelectedTypesArray = checked ? [...JOB_TYPES_CONFIG.map(t => t.id), ALL_TYPES_OPTION.id] : [];
    } else {
      const otherSelectedTypes = selectedTypes.filter(id => id !== ALL_TYPES_OPTION.id);
      let currentIndividualSelections = checked
        ? [...otherSelectedTypes, typeId]
        : otherSelectedTypes.filter(id => id !== typeId);

      currentIndividualSelections = Array.from(new Set(currentIndividualSelections));

      const allOtherTypesSelected =
        JOB_TYPES_CONFIG.length > 0 && JOB_TYPES_CONFIG.every(t => currentIndividualSelections.includes(t.id));

      if (allOtherTypesSelected) {
        newSelectedTypesArray = [...currentIndividualSelections, ALL_TYPES_OPTION.id];
      } else {
        newSelectedTypesArray = currentIndividualSelections;
      }
    }

    const finalSelectedTypes = Array.from(new Set(newSelectedTypesArray));
    setSelectedTypes(finalSelectedTypes);
  };

  const handleSearchFieldChange = (value: string) => {
    setSearchField(value);
    setSearchValue('');
  };

  const handleSearchValueChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSearchValue(event.target.value);
  };

  const executeSearch = () => {
    updateSearchParams(selectedTypes);
  };

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      executeSearch();
    }
  };

  const getSelectedTypesLabel = () => {
    if (selectedTypes.includes(ALL_TYPES_OPTION.id)) return ALL_TYPES_OPTION.label;
    if (selectedTypes.length === 0) return 'Job Type';
    if (selectedTypes.length === 1) {
      const foundType = JOB_TYPES_CONFIG.find(t => t.id === selectedTypes[0]);
      return foundType ? foundType.label : 'Job Type';
    }
    return `${selectedTypes.length} types selected`;
  };

  return (
    <div className='flex flex-col gap-2 rounded-md @md:flex-row'>
      <div className='flex flex-1 flex-row gap-2'>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant='outline'
              className='data-[state=open]:bg-accent h-9 flex-1 justify-between text-xs focus:ring-0 focus:ring-offset-0'
            >
              {getSelectedTypesLabel()}
              <ChevronsUpDown className='ml-2 h-4 w-4 shrink-0 opacity-50' />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent className='w-[var(--radix-dropdown-menu-trigger-width)]'>
            <DropdownMenuSeparator />
            <DropdownMenuCheckboxItem
              key={ALL_TYPES_OPTION.id}
              checked={selectedTypes.includes(ALL_TYPES_OPTION.id)}
              onCheckedChange={checked => handleSelectedTypesChange(ALL_TYPES_OPTION.id, !!checked)}
              onSelect={e => e.preventDefault()}
              className='text-xs'
            >
              {ALL_TYPES_OPTION.label}
            </DropdownMenuCheckboxItem>
            <DropdownMenuSeparator />
            {JOB_TYPES_CONFIG.map(jobType => (
              <DropdownMenuCheckboxItem
                key={jobType.id}
                checked={selectedTypes.includes(jobType.id)}
                onCheckedChange={checked => handleSelectedTypesChange(jobType.id, !!checked)}
                disabled={selectedTypes.includes(ALL_TYPES_OPTION.id)}
                onSelect={e => e.preventDefault()}
                className='text-xs'
              >
                {jobType.label}
              </DropdownMenuCheckboxItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        <Select value={searchField} onValueChange={handleSearchFieldChange}>
          <SelectTrigger className='h-9 flex-1 text-xs focus:ring-0 focus:ring-offset-0'>
            <SelectValue placeholder='Search By' />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value='title' className='text-xs'>
              Title
            </SelectItem>
            <SelectItem value='name' className='text-xs'>
              User
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className='flex flex-1 flex-col gap-2 md:flex-row md:items-center'>
        <Input
          type='text'
          placeholder={searchField === 'title' ? 'Search by title...' : 'Search by user name...'}
          value={searchValue}
          onChange={handleSearchValueChange}
          onKeyDown={handleKeyDown}
          className='rtext-xs h-9 flex-grow focus:ring-0 focus:ring-offset-0 sm:text-sm'
        />
        <Button onClick={executeSearch} size='sm' className='h-9 px-3 text-xs sm:text-sm' aria-label='Search'>
          <SearchIcon className='h-4 w-4' />
        </Button>
      </div>
    </div>
  );
};

export default JobSearchInput;
