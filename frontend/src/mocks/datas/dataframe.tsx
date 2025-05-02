import { ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { MUser } from '@/mocks/datas/user';
import { TMachine } from '@/types/job';
import { Job } from '@/types/scheduler';

export const machineColumns: ColumnDef<TMachine>[] = [
  {
    accessorKey: 'machineId',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          MachineId
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
  {
    accessorKey: 'parameter',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          Parameter
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
  {
    accessorKey: 'value',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          Value
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
  {
    accessorKey: 'unit',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          Unit
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
  {
    accessorKey: 'collectedAt',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          CollectedAt
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
];

export const MMachineTable: TMachine[] = [
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'temperature',
    value: 72.5,
    unit: '°C',
    collectedAt: '2025-04-22T09:44:58Z',
  },
  {
    machineId: 'MACH-003',
    parameter: 'pressure',
    value: 3.1,
    unit: 'bar',
    collectedAt: '2025-04-23T04:21:32Z',
  },
  {
    machineId: 'MACH-001',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T08:41:21Z',
  },
  {
    machineId: 'MACH-002',
    parameter: 'speed',
    value: 1200,
    unit: 'rpm',
    collectedAt: '2025-04-23T09:44:59Z',
  },
];

export const jobColumns: ColumnDef<Job>[] = [
  {
    accessorKey: 'title',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          Title
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
  {
    accessorKey: 'sourceData',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          Source Data
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
  {
    accessorKey: 'createdAt',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          Date
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
  {
    accessorKey: 'user',
    header: ({ column }) => {
      return (
        <Button
          variant='ghost'
          onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
          className='cursor-pointer'
        >
          User
          <ArrowUpDown className='ml-2 h-4 w-4' />
        </Button>
      );
    },
  },
];

export const MJobTable: Job[] = [
  {
    title: 'job title 1',
    description: 'job description 1',
    createdAt: '2025-04-22T09:44:58Z',
    jobId: '1',
    commandList: [],
    sourceData: 'sourceData 1',
    userName: MUser.name,
  },
  {
    title: 'job title 2',
    description: 'job description 2',
    createdAt: '2025-04-22T09:44:58Z',
    jobId: '2',
    commandList: [],
    sourceData: 'sourceData 2',
    userName: MUser.name,
  },
  {
    title: 'job title 3',
    description: 'job description 3',
    createdAt: '2025-04-22T09:44:58Z',
    jobId: '3',
    commandList: [],
    sourceData: 'sourceData 3',
    userName: MUser.name,
  },
  {
    title: 'job title 4',
    description: 'job description 4',
    createdAt: '2025-04-22T09:44:58Z',
    jobId: '4',
    commandList: [],
    sourceData: 'sourceData 4',
    userName: MUser.name,
  },
  {
    title: 'job title 5',
    description: 'job description 5',
    createdAt: '2025-04-22T09:44:58Z',
    jobId: '5',
    commandList: [],
    sourceData: 'sourceData 5',
    userName: MUser.name,
  },
  {
    title: 'job title 6',
    description: 'job description 6',
    createdAt: '2025-04-22T09:44:58Z',
    jobId: '6',
    commandList: [],
    sourceData: 'sourceData 6',
    userName: MUser.name,
  },
];
