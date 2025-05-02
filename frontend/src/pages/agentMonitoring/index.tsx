import { useState } from 'react';

import DataTable from '@/components/DataTable';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { JOB_TYPE } from '@/constant/job';
import { DEPARTMENT } from '@/constant/user';
import useClickOutsideRef from '@/hooks/useClickOutsideRef';
import { MJobTable, jobColumns } from '@/mocks/datas/dataframe';
import { MUserNameList } from '@/mocks/datas/user';
import { TDepartment, TJobType } from '@/types/agent';

const AgentMonitoringPage: React.FC = () => {
  const [jobType, setJobType] = useState<TJobType>();
  const [department, setDepartment] = useState<TDepartment>();
  const [name, setName] = useState<string>('');

  const [searchNameList] = useState<string[]>(MUserNameList);
  const [isOpenScrollArea, setIsOpenScrollArea] = useState<boolean>(false);

  const scrollAreaRef = useClickOutsideRef<HTMLDivElement>(() =>
    setIsOpenScrollArea(false),
  );

  const handleSearchName = () => {
    if (name.trim() === '') return;

    setIsOpenScrollArea(true);
  };

  const handleSearchJobList = () => {};

  return (
    <div className='flex w-full flex-col gap-4 p-8'>
      <div className='flex items-center gap-4'>
        <div className='flex-1'>
          <Select value={jobType} onValueChange={setJobType}>
            <SelectTrigger className='w-full'>
              <SelectValue placeholder='Job Type' />
            </SelectTrigger>
            <SelectContent>
              {Object.values(JOB_TYPE).map((job, index) => (
                <SelectItem key={`${job}-${index}`} value={job}>
                  {job}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className='flex-1'>
          <Select value={department} onValueChange={setDepartment}>
            <SelectTrigger className='w-full'>
              <SelectValue placeholder='Department' />
            </SelectTrigger>
            <SelectContent>
              {Object.values(DEPARTMENT).map((department, index) => (
                <SelectItem key={`${department}-${index}`} value={department}>
                  {department}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div ref={scrollAreaRef} className='relative h-full flex-2'>
          <Input
            value={name}
            onChange={e => setName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSearchName()}
            placeholder='Search employee name'
          />

          {isOpenScrollArea && (
            <div className='absolute top-full left-0 z-10 w-full translate-y-1'>
              <ScrollArea className='h-[166px] rounded-md border bg-white'>
                <ul className='divide flex flex-col divide-y-1 divide-gray-400'>
                  {searchNameList.map((name, index) => (
                    <li
                      key={`${name}-${index}`}
                      className='cursor-pointer px-2 py-1 hover:bg-black/2'
                      onClick={handleSearchJobList}
                    >
                      {name}
                    </li>
                  ))}
                </ul>
              </ScrollArea>
            </div>
          )}
        </div>
        <Button onClick={handleSearchName} className='cursor-pointer'>
          Search
        </Button>
      </div>

      <div className='flex-1'>
        <DataTable columns={jobColumns} data={MJobTable} />
      </div>
    </div>
  );
};

export default AgentMonitoringPage;
