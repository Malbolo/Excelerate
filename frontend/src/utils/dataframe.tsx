import { ColumnDef } from '@tanstack/react-table';
import { ArrowUpDown } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { DataFrameRow } from '@/types/dataframe';

export function createSortableColumns(
  data: Record<string, any>,
): ColumnDef<DataFrameRow>[] {
  return Object.keys(data).map(key => ({
    accessorKey: key,
    header: ({ column }) => (
      <Button
        variant='ghost'
        onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}
        className='cursor-pointer'
      >
        {key}
        <ArrowUpDown className='ml-2 h-4 w-4' />
      </Button>
    ),
  }));
}
