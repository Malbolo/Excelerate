interface CommandItem {
  commandTitle: string;
}

const CommandItem = ({ commandTitle }: CommandItem) => {
  return (
    <div className='flex items-center justify-between'>
      <div className='flex grow items-center gap-2 pr-2'>
        <div className='bg-success h-4 w-4 shrink-0 rounded-full' />
        <p>{commandTitle}</p>
      </div>
    </div>
  );
};

export default CommandItem;
