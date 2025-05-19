import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface OutputDisplayProps {
  templateOutput: string;
  modifiedOutput: string;
}

const OutputDisplay = ({ templateOutput, modifiedOutput }: OutputDisplayProps) => {
  return (
    <div className='flex w-2/5 flex-col gap-3 overflow-y-auto xl:w-1/3'>
      <Card className='flex flex-1 flex-col'>
        <CardHeader className='p-3'>
          <CardTitle className='text-sm font-semibold text-gray-700'>Original AI Output (Template Example)</CardTitle>
        </CardHeader>
        <CardContent className='flex-1 overflow-y-auto p-3 text-xs whitespace-pre-wrap text-gray-600'>
          {templateOutput ? (
            templateOutput
          ) : (
            <p className='italic'>AI output based on initial template parameters could appear here.</p>
          )}
        </CardContent>
      </Card>

      <Card className='flex flex-1 flex-col'>
        <CardHeader className='p-3'>
          <CardTitle className='text-sm font-semibold text-gray-700'>AI Output (Test Result)</CardTitle>
        </CardHeader>
        <CardContent className='flex-1 overflow-y-auto p-3 text-xs whitespace-pre-wrap text-gray-600'>
          {modifiedOutput ? modifiedOutput : <p className='italic'>AI output will appear here after testing.</p>}
        </CardContent>
      </Card>
    </div>
  );
};

export default OutputDisplay;
