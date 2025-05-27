import ClipLoader from 'react-spinners/ClipLoader';

const Loading = () => {
  return (
    <div className='flex h-full w-full items-center justify-center'>
      <ClipLoader size={18} color='#7d9ecd' />
    </div>
  );
};

export default Loading;
