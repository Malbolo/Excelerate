import { Trash2 } from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface FewShot {
  human: string;
  ai: string;
  index: number;
}

interface FewShotItemEditorProps {
  fs: FewShot;
  itemIndex: number;
  onFewShotChange: (internalIndex: number, field: 'human' | 'ai', value: string) => void;
  onRemoveFewShot: (internalIndex: number) => void;
}

const FewShotItemEditor = ({ fs, itemIndex, onFewShotChange, onRemoveFewShot }: FewShotItemEditorProps) => {
  return (
    <div key={fs.index} className='rounded-md border p-3'>
      <div className='mb-2 flex items-center justify-between'>
        <Badge variant='secondary' className='m-1'>
          Example {itemIndex + 1}
        </Badge>
        <Button
          variant='ghost'
          size='icon'
          onClick={() => onRemoveFewShot(fs.index)}
          className='h-6 w-6 text-red-500 hover:bg-red-100 hover:text-red-600'
          aria-label='Remove few-shot'
        >
          <Trash2 className='h-3.5 w-3.5' />
        </Button>
      </div>
      <div className='space-y-2.5'>
        <div>
          <Label htmlFor={`fs-user-${fs.index}`} className='mb-2 ml-1 block text-xs font-medium text-gray-700'>
            User Input (Example)
          </Label>
          <Textarea
            id={`fs-user-${fs.index}`}
            value={fs.human}
            onChange={e => onFewShotChange(fs.index, 'human', e.target.value)}
            placeholder='User says...'
            className='min-h-[70px] resize-none rounded-md text-sm'
            rows={3}
          />
        </div>
        <div>
          <Label htmlFor={`fs-ai-${fs.index}`} className='mb-2 ml-1 block text-xs font-medium text-gray-700'>
            AI Response (Example)
          </Label>
          <Textarea
            id={`fs-ai-${fs.index}`}
            value={fs.ai}
            onChange={e => onFewShotChange(fs.index, 'ai', e.target.value)}
            placeholder='AI responds...'
            className='min-h-[70px] resize-none rounded-md text-sm'
            rows={3}
          />
        </div>
      </div>
    </div>
  );
};

export default FewShotItemEditor;
