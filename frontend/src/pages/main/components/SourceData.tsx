import { cn } from '@/lib/utils';
import { useSourceStore } from '@/store/useSourceStore';

const SourceData = () => {
  const { sourceDataCommand, sourceParams } = useSourceStore();

  return (
    <section className='flex flex-1 flex-col justify-between'>
      <div className='flex items-baseline justify-between'>
        <p className='py-1 text-lg font-bold'>Source Data</p>
        {sourceDataCommand && (
          <p className='ml-2 flex-1 truncate text-right text-xs text-gray-500'>
            {sourceDataCommand}
          </p>
        )}
      </div>
      <div className='card-gradient flex grow flex-col overflow-hidden rounded-xl border bg-white'>
        {sourceParams && Object.keys(sourceParams).length > 0 ? (
          <div className='flex h-full flex-col'>
            <div className='sticky top-0 z-10 flex rounded-t-xl border-b bg-white'>
              <div className='w-[35%] flex-shrink-0 rounded-tl-xl bg-slate-100 px-1.5 py-2 text-xs font-semibold text-slate-700'>
                Key
              </div>
              <div className='flex-grow rounded-tr-xl bg-slate-100 px-1.5 py-2 text-xs font-semibold text-slate-700'>
                Value
              </div>
            </div>
            <div className='flex-1 overflow-y-auto px-1.5'>
              {Object.entries(sourceParams).map(([key, value], index) => (
                <div
                  key={key}
                  className={cn(
                    'flex border-b border-slate-100',
                    index % 2 === 0 ? 'bg-white' : 'bg-slate-50/50',
                    'hover:bg-blue-50/50',
                  )}
                >
                  <div className='w-[35%] flex-shrink-0 px-2 py-2 text-xs font-semibold text-slate-800'>
                    <span className='inline-flex items-center rounded-md bg-slate-100 px-1.5 py-0.5 text-xs font-medium text-slate-700 ring-1 ring-slate-200/80 ring-inset'>
                      {key}
                    </span>
                  </div>
                  <div className='flex-grow px-2 py-2 text-xs break-all text-slate-700'>
                    {typeof value === 'object' ? (
                      <pre className='rounded bg-slate-50 p-1.5 font-mono text-xs whitespace-pre-wrap'>
                        {JSON.stringify(value, null, 2)}
                      </pre>
                    ) : (
                      <span className='inline-flex items-center rounded-md bg-blue-50 px-1.5 py-0.5 text-xs font-medium text-blue-700 ring-1 ring-blue-200/80 ring-inset'>
                        {String(value)}
                      </span>
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
                <p className='text-sm text-gray-500'>
                  파라미터 정보가 없습니다.
                </p>
              )}
          </div>
        )}
      </div>
    </section>
  );
};

export default SourceData;
