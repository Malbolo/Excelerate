import { useSourceStore } from '@/store/useSourceStore';

const SourceData = () => {
  const { sourceDataCommand } = useSourceStore();

  return (
    <section className='flex flex-1 flex-col justify-between'>
      <p className='py-1 text-lg font-bold'>Source Data</p>
      <div className='card-gradient flex h-38 flex-col items-center justify-center overflow-y-auto rounded-xl border p-4'>
        {sourceDataCommand ? (
          <p>{sourceDataCommand}</p>
        ) : (
          <div className='flex flex-col items-center gap-2 text-gray-500'>
            <p>Source data hasn't been loaded.</p>
            <p>Please load it using a command.</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default SourceData;
