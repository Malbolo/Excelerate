import { ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { TMachine } from '@/types/job';

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

export const MMachine: TMachine[] = [
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
