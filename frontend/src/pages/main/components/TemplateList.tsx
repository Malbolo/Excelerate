interface TemplateListProps {
  templates: string[];
}

const TemplateList: React.FC<TemplateListProps> = ({ templates }) => {
  return (
    <section className='flex max-h-48 flex-1 flex-col gap-2'>
      <p className='text-lg font-bold'>Template List</p>
      <div className='flex grow flex-col gap-4 overflow-y-auto border border-black p-2'>
        <ul className='list-inside list-disc'>
          {templates.map(template => (
            <li key={template}>{template}</li>
          ))}
        </ul>
      </div>
    </section>
  );
};

export default TemplateList;
