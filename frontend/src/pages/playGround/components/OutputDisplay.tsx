import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface OutputDisplayProps {
  templateOutput: string;
  modifiedOutput: string;
}

const OutputDisplay = ({ templateOutput, modifiedOutput }: OutputDisplayProps) => {
  return (
    <div className='flex w-2/5 flex-col gap-3 overflow-y-auto'>
      <Card className='flex flex-1 flex-col py-8'>
        <CardHeader>
          <CardTitle className='text-sm font-bold'>Original AI Output (Template Example)</CardTitle>
        </CardHeader>
        <CardContent className='flex-1 overflow-y-auto text-xs whitespace-pre-wrap'>
          {templateOutput ? (
            templateOutput
          ) : (
            <p className='italic'>AI output based on initial template parameters could appear here.</p>
          )}
        </CardContent>
      </Card>

      <Card className='flex flex-1 flex-col py-8'>
        <CardHeader>
          <CardTitle className='text-sm font-bold'>AI Output (Test Result)</CardTitle>
        </CardHeader>
        <CardContent className='flex-1 overflow-y-auto text-xs whitespace-pre-wrap'>
          {modifiedOutput ? modifiedOutput : <p className='italic'>AI output will appear here after testing.</p>}
        </CardContent>
      </Card>
    </div>
  );
};

export default OutputDisplay;
