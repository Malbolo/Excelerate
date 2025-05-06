import { useState } from 'react';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from '@/components/ui/pagination';
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
import useInternalRouter from '@/hooks/useInternalRouter';
import { MJobTable } from '@/mocks/datas/dataframe';
import { MUserNameList } from '@/mocks/datas/user';
import { TDepartment, TJobType } from '@/types/agent';

const AgentMonitoringPage: React.FC = () => {
  const [jobType, setJobType] = useState<TJobType>();
  const [department, setDepartment] = useState<TDepartment>();
  const [name, setName] = useState<string>('');

  const [searchNameList] = useState<string[]>(MUserNameList);
  const [isOpenScrollArea, setIsOpenScrollArea] = useState<boolean>(false);

  const PAGE_SIZE = 4;
  const [page, setPage] = useState(1);
  const totalPages = Math.ceil(MJobTable.length / PAGE_SIZE);
  const pagedJobs = MJobTable.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const { push } = useInternalRouter();

  const scrollAreaRef = useClickOutsideRef<HTMLDivElement>(() =>
    setIsOpenScrollArea(false),
  );

  const handleSearchName = () => {
    if (name.trim() === '') return;

    setIsOpenScrollArea(true);
  };

  const handleSearchJobList = () => {};

  return (
    <div className='flex h-screen w-full flex-col justify-between gap-5 p-8'>
      <div className='flex items-center gap-4'>
        <div className='flex-1'>
          <Select
            value={jobType || ''}
            onValueChange={(value: string) => setJobType(value as TJobType)}
          >
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

      <section className='flex flex-1 flex-col gap-4'>
        {pagedJobs.map(job => (
          <Card
            key={job.jobId}
            onClick={() => push(`/agent-monitoring/job/${job.jobId}`)}
            className='cursor-pointer p-5'
          >
            <CardHeader>
              <CardTitle>{job.title}</CardTitle>
              <CardDescription>{job.description}</CardDescription>
            </CardHeader>
            <CardContent className='flex w-full justify-between'>
              <p>{job.userName}</p>
              <p>{job.createdAt}</p>
            </CardContent>
          </Card>
        ))}
      </section>

      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => setPage(p => Math.max(1, p - 1))}
              aria-disabled={page === 1}
            />
          </PaginationItem>
          {Array.from({ length: totalPages }).map((_, index) => (
            <PaginationItem key={index}>
              <PaginationLink
                isActive={page === index + 1}
                onClick={() => setPage(index + 1)}
              >
                {index + 1}
              </PaginationLink>
            </PaginationItem>
          ))}
          <PaginationItem>
            <PaginationNext
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              aria-disabled={page === totalPages}
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  );
};

export default AgentMonitoringPage;
