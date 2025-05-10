import { useSourceStore } from '@/store/useSourceStore';

const SourceData: React.FC = () => {
  const { sourceDataCommand } = useSourceStore();

  return (
    <section className='flex max-h-48 flex-1 flex-col gap-4'>
      <p className='text-lg font-bold'>Source Data</p>
      <div className='card-gradient flex grow flex-col items-center justify-center overflow-y-auto rounded-xl border p-4'>
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
