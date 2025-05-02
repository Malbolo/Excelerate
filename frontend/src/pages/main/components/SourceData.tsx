interface SourceDataProps {
  sourceData?: string;
}

const SourceData: React.FC<SourceDataProps> = ({ sourceData = '' }) => {
  return (
    <section className='flex max-h-48 flex-1 flex-col gap-2'>
      <p className='text-lg font-bold'>Source Data</p>
      <div className='flex grow flex-col justify-center border border-black p-2 text-center'>
        {sourceData ? (
          <p>{sourceData}</p>
        ) : (
          <>
            <p>Source data hasn't been loaded.</p>
            <p>Please load it using a command.</p>
          </>
        )}
      </div>
    </section>
  );
};

export default SourceData;
