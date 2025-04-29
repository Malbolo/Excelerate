import { TMachine } from '@/types/job';
import { ColumnDef } from '@tanstack/react-table';

export const machineColumns: ColumnDef<TMachine>[] = [
  {
    accessorKey: 'machineId',
    header: 'machineId',
  },
  {
    accessorKey: 'parameter',
    header: 'parameter',
  },
  {
    accessorKey: 'value',
    header: 'value',
  },
  {
    accessorKey: 'unit',
    header: 'unit',
  },
  {
    accessorKey: 'collectedAt',
    header: 'collectedAt',
  },
];

export const MMachine: TMachine[] = [
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "temperature",
    "value": 72.5,
    "unit": "°C",
    "collectedAt": "2025-04-22T09:44:58Z"
  },
  {
    "machineId": "MACH-003",
    "parameter": "pressure",
    "value": 3.1,
    "unit": "bar",
    "collectedAt": "2025-04-23T04:21:32Z"
  },
  {
    "machineId": "MACH-001",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T08:41:21Z"
  },
  {
    "machineId": "MACH-002",
    "parameter": "speed",
    "value": 1200,
    "unit": "rpm",
    "collectedAt": "2025-04-23T09:44:59Z"
  },
];
