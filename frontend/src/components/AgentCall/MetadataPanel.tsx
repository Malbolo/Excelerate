import { Log, LogMetadata } from '@/types/agent';

import { Badge } from '../ui/badge';

interface MetadataItemProps {
  label: string;
  value: LogMetadata | string | number | null;
  depth?: number;
}

const MetadataItem = ({ label, value, depth = 0 }: MetadataItemProps) => {
  if (value === null) return null;

  if (typeof value === 'object') {
    return (
      <div className='flex flex-col gap-2'>
        <div className='flex items-center gap-2'>
          <Badge variant='outline' className='font-medium'>
            {label}
          </Badge>
        </div>
        <div className='ml-4 flex flex-col gap-2 border-l border-gray-200 pl-4'>
          {Object.entries(value).map(([key, val]) => (
            <MetadataItem key={key} label={key} value={val} depth={depth + 1} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className='flex items-center gap-2'>
      <Badge variant='secondary' className='font-medium'>
        {label}
      </Badge>
      <span className='text-xs text-gray-600'>{String(value)}</span>
    </div>
  );
};

const MetadataPanel = ({ metadata }: Pick<Log, 'metadata'>) => {
  if (!metadata || Object.keys(metadata).length === 0) {
    return (
      <div className='flex items-center justify-center rounded-tl-md rounded-b-md'>
        <p className='text-sm text-gray-500'>No metadata available</p>
      </div>
    );
  }

  return (
    <div className='flex overflow-y-auto rounded-tl-md rounded-b-md'>
      <div className='flex w-full flex-col gap-4 px-4 py-5'>
        <div className='flex flex-col gap-4'>
          <div className='flex items-center gap-2'>
            <Badge variant='outline' className='font-medium'>
              Metadata
            </Badge>
          </div>
          <div className='ml-4 flex flex-col gap-4 border-l border-gray-200 pl-4'>
            {Object.entries(metadata).map(([key, value]) => (
              <MetadataItem key={key} label={key} value={value} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetadataPanel;
