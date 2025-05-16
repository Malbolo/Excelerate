import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useSourceStore } from '@/store/useSourceStore';

const SourceData = () => {
  const { sourceDataCommand, sourceParams } = useSourceStore();

  return (
    <section className='flex min-w-1/2 flex-1 flex-col justify-between gap-2 pl-2'>
      <div className='flex items-baseline justify-between'>
        <p className='py-1 text-lg font-bold'>Source Data</p>
        {sourceDataCommand && (
          <p className='ml-2 flex-1 truncate text-right text-xs text-gray-500'>
            {sourceDataCommand}
          </p>
        )}
      </div>
      <div className='card-gradient flex h-38 flex-col overflow-hidden rounded-xl border bg-white'>
        {sourceParams && Object.keys(sourceParams).length > 0 ? (
          <div className='flex h-full flex-col'>
            <div className='sticky top-0 z-10 flex rounded-t-xl border-b bg-slate-100 font-bold'>
              <div className='w-1/2 flex-shrink-0 rounded-tl-xl px-4 py-2 text-xs font-semibold text-slate-700'>
                Key
              </div>
              <div className='flex-grow rounded-tr-xl px-2 py-2 text-xs font-semibold text-slate-700'>
                Value
              </div>
            </div>
            <div className='h-full flex-1 divide-y overflow-y-auto'>
              {Object.entries(sourceParams).map(([key, value], index) => (
                <div
                  key={key}
                  className={cn(
                    'flex border-slate-100',
                    index % 2 === 0 ? 'bg-white' : 'bg-slate-50/50',
                    'hover:bg-blue-50/50',
                  )}
                >
                  <div className='w-1/2 flex-shrink-0 px-3 py-2 text-xs font-semibold text-slate-800'>
                    <Badge variant='outline'>{key}</Badge>
                  </div>
                  <div className='flex-grow px-3 py-2 text-xs break-all text-slate-700'>
                    {typeof value === 'object' ? (
                      <Badge variant='destructive'>
                        {JSON.stringify(value, null, 2)}
                      </Badge>
                    ) : (
                      <Badge variant='secondary'>{String(value)}</Badge>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className='flex flex-1 flex-col items-center justify-center p-4 text-center'>
            {!sourceDataCommand && (
              <>
                <p className='text-sm font-medium text-gray-700'>
                  Source data hasn't been loaded.
                </p>
                <p className='mt-1 text-xs text-gray-500'>
                  Please load it using a command.
                </p>
              </>
            )}
            {sourceDataCommand &&
              (!sourceParams || Object.keys(sourceParams).length === 0) && (
                <p className='text-sm text-gray-500'>No Parameter.</p>
              )}
          </div>
        )}
      </div>
    </section>
  );
};

export default SourceData;
