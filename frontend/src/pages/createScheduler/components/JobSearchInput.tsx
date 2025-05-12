import { ChangeEvent, KeyboardEvent, useEffect, useState } from 'react';

import { ChevronsUpDown, SearchIcon } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

const JOB_TYPES_CONFIG = [
  { id: 'CNC Assy G', label: 'CNC Assy G' },
  { id: 'CNC Prod 1G', label: 'CNC Prod 1G' },
  { id: 'CNC Prod 3G', label: 'CNC Prod 3G' },
  { id: 'CNC Prod 4G', label: 'CNC Prod 4G' },
  { id: 'CNC MEG G', label: 'CNC MEG G' },
];

const ALL_TYPES_OPTION = { id: 'all', label: 'All Types' };

const JobSearchInput = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const initialTypesString = searchParams.get('types') || '';
  const initialSelectedTypes = initialTypesString
    ? initialTypesString.split(',')
    : [];

  let determinedInitialSearchField = 'title';
  let determinedInitialSearchQuery = '';

  if (searchParams.has('title')) {
    determinedInitialSearchField = 'title';
    determinedInitialSearchQuery = searchParams.get('title') || '';
  } else if (searchParams.has('name')) {
    determinedInitialSearchField = 'user';
    determinedInitialSearchQuery = searchParams.get('name') || '';
  }

  const [selectedTypes, setSelectedTypes] =
    useState<string[]>(initialSelectedTypes);
  const [searchField, setSearchField] = useState<string>(
    determinedInitialSearchField,
  );
  const [searchValue, setSearchValue] = useState<string>(
    determinedInitialSearchQuery,
  );

  useEffect(() => {
    const currentTypesString = searchParams.get('types') || '';
    const currentSelectedTypesFromParams = currentTypesString
      ? currentTypesString.split(',')
      : [];

    let currentInferredSearchField = 'title';
    let currentInferredSearchValue = '';

    if (searchParams.has('title')) {
      currentInferredSearchField = 'title';
      currentInferredSearchValue = searchParams.get('title') || '';
    } else if (searchParams.has('name')) {
      currentInferredSearchField = 'user';
      currentInferredSearchValue = searchParams.get('name') || '';
    }

    if (
      JSON.stringify(selectedTypes.sort()) !==
      JSON.stringify(currentSelectedTypesFromParams.sort())
    ) {
      setSelectedTypes(currentSelectedTypesFromParams);
    }
    if (searchField !== currentInferredSearchField) {
      setSearchField(currentInferredSearchField);
    }
    if (searchValue !== currentInferredSearchValue) {
      setSearchValue(currentInferredSearchValue);
    }
  }, [searchParams]);

  const updateSearchParams = (updatedTypes: string[]) => {
    setSearchParams(
      prev => {
        const newParams = new URLSearchParams(prev.toString());
        newParams.delete('title');
        newParams.delete('name');

        const trimmedSearchValue = searchValue.trim();
        if (trimmedSearchValue) {
          if (searchField === 'user') {
            newParams.set('name', trimmedSearchValue);
          } else {
            newParams.set('title', trimmedSearchValue);
          }
        } else {
          newParams.delete('name');
          newParams.delete('title');
        }

        if (updatedTypes.length > 0) {
          newParams.set('types', updatedTypes.join(','));
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
    let newSelectedTypes: string[];

    if (typeId === ALL_TYPES_OPTION.id) {
      newSelectedTypes = checked
        ? [...JOB_TYPES_CONFIG.map(t => t.id), ALL_TYPES_OPTION.id]
        : [];
    } else {
      const otherSelectedTypes = selectedTypes.filter(
        id => id !== ALL_TYPES_OPTION.id,
      );
      let currentIndividualSelections = checked
        ? [...otherSelectedTypes, typeId]
        : otherSelectedTypes.filter(id => id !== typeId);

      currentIndividualSelections = Array.from(
        new Set(currentIndividualSelections),
      );

      const allOtherTypesSelected = JOB_TYPES_CONFIG.every(t =>
        currentIndividualSelections.includes(t.id),
      );

      if (allOtherTypesSelected) {
        newSelectedTypes = [
          ...currentIndividualSelections,
          ALL_TYPES_OPTION.id,
        ];
      } else {
        newSelectedTypes = currentIndividualSelections;
      }
    }

    const finalSelectedTypes = Array.from(new Set(newSelectedTypes));
    setSelectedTypes(finalSelectedTypes);
    updateSearchParams(finalSelectedTypes);
  };

  const handleSearchFieldChange = (value: string) => {
    setSearchField(value);
    setSearchValue('');
    setSearchParams(
      prev => {
        const newParams = new URLSearchParams(prev.toString());
        newParams.delete('title');
        newParams.delete('name');
        if (value === 'user' && searchValue.trim())
          newParams.set('name', searchValue.trim());
        else if (value === 'title' && searchValue.trim())
          newParams.set('title', searchValue.trim());
        newParams.set('page', '1');
        return newParams;
      },
      { replace: true },
    );
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
    if (selectedTypes.includes(ALL_TYPES_OPTION.id))
      return ALL_TYPES_OPTION.label;
    if (selectedTypes.length === 0) return 'Job Type';
    if (selectedTypes.length === 1) {
      const foundType = JOB_TYPES_CONFIG.find(t => t.id === selectedTypes[0]);
      return foundType ? foundType.label : 'Job Type';
    }
    return `${selectedTypes.length} types selected`;
  };

  return (
    <div className='flex flex-col gap-4 rounded-md border p-4 md:flex-row md:items-start'>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant='outline'
            className='data-[state=open]:bg-accent h-9 w-full justify-between text-xs focus:ring-0 focus:ring-offset-0 sm:text-sm md:w-auto md:min-w-[200px]'
          >
            {getSelectedTypesLabel()}
            <ChevronsUpDown className='ml-2 h-4 w-4 shrink-0 opacity-50' />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className='w-[--radix-dropdown-menu-trigger-width]'>
          <DropdownMenuLabel>Select Job Types</DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuCheckboxItem
            key={ALL_TYPES_OPTION.id}
            checked={selectedTypes.includes(ALL_TYPES_OPTION.id)}
            onCheckedChange={checked =>
              handleSelectedTypesChange(ALL_TYPES_OPTION.id, !!checked)
            }
            onSelect={e => e.preventDefault()}
          >
            {ALL_TYPES_OPTION.label}
          </DropdownMenuCheckboxItem>
          <DropdownMenuSeparator />
          {JOB_TYPES_CONFIG.map(jobType => (
            <DropdownMenuCheckboxItem
              key={jobType.id}
              checked={selectedTypes.includes(jobType.id)}
              onCheckedChange={checked =>
                handleSelectedTypesChange(jobType.id, !!checked)
              }
              disabled={selectedTypes.includes(ALL_TYPES_OPTION.id)}
              onSelect={e => e.preventDefault()}
            >
              {jobType.label}
            </DropdownMenuCheckboxItem>
          ))}
        </DropdownMenuContent>
      </DropdownMenu>

      <div className='flex flex-grow flex-col gap-2 md:flex-row md:items-center'>
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
    </div>
  );
};

export default JobSearchInput;
