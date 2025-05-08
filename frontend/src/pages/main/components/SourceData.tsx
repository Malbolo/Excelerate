interface SourceDataProps {
  sourceData?: string;
}

const SourceData: React.FC<SourceDataProps> = ({ sourceData = '' }) => {
  return (
    <section className='flex max-h-48 flex-1 flex-col gap-4'>
      <p className='text-lg font-bold text-gray-900'>Source Data</p>
      <div className='flex grow flex-col justify-center overflow-y-auto rounded-xl border border-[#E5E7EB] bg-gradient-to-b from-white to-[#F8FAFF] p-4 [&::-webkit-scrollbar]:w-2 [&::-webkit-scrollbar-thumb]:rounded-full [&::-webkit-scrollbar-thumb]:bg-[#034EA2]/30 hover:[&::-webkit-scrollbar-thumb]:bg-[#034EA2]/50 [&::-webkit-scrollbar-track]:rounded-full [&::-webkit-scrollbar-track]:bg-gray-100'>
        {sourceData ? (
          <p className='text-gray-700'>{sourceData}</p>
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
