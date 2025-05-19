// src/components/playground/PromptEditor.tsx
import { PlusIcon, Send } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';

import FewShotItemEditor from './FewShotItemEditor';

interface FewShot {
  human: string;
  ai: string;
  index: number;
}

interface PromptEditorProps {
  systemPrompt: string;
  onSystemPromptChange: (value: string) => void;
  fewShots: FewShot[];
  onAddFewShot: () => void;
  onRemoveFewShot: (indexToRemove: number) => void;
  onFewShotChange: (internalIndex: number, field: 'human' | 'ai', value: string) => void;
  userInput: string;
  onUserInputchange: (value: string) => void;
  onTest: () => void;
  onOpenVariablesDialog: () => void;
  variableKeysCount: number;
  isTestDisabled: boolean;
}

const PromptEditor = ({
  systemPrompt,
  onSystemPromptChange,
  fewShots,
  onAddFewShot,
  onRemoveFewShot,
  onFewShotChange,
  userInput,
  onUserInputchange,
  onTest,
  onOpenVariablesDialog,
  variableKeysCount,
  isTestDisabled,
}: PromptEditorProps) => {
  return (
    <div className='w-3/5 overflow-y-auto rounded-lg border bg-white p-0.5 shadow-sm xl:w-2/3'>
      <div className='space-y-5 p-4'>
        <div>
          <Label htmlFor='system-prompt' className='mb-1 block text-xs font-medium text-gray-700'>
            System Prompt
          </Label>
          <Textarea
            id='system-prompt'
            value={systemPrompt}
            onChange={e => onSystemPromptChange(e.target.value)}
            placeholder='Define the AI behavior and context here...'
            className='min-h-[100px] resize-none rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500'
            rows={4}
          />
        </div>
        <Separator />
        <div>
          <div className='mb-2.5 flex items-center justify-between'>
            <h3 className='text-xs font-medium text-gray-700'>Few-shot Prompts (Examples)</h3>
            <Button
              variant='outline'
              size='sm'
              onClick={onAddFewShot}
              className='flex items-center gap-1 border-blue-500 py-1 text-xs text-blue-600 hover:bg-blue-50 hover:text-blue-700'
            >
              <PlusIcon className='h-3.5 w-3.5' />
              Add Example
            </Button>
          </div>
          <div className='space-y-3'>
            {fewShots.map((fs, index) => (
              <FewShotItemEditor
                key={fs.index}
                fs={fs}
                itemIndex={index}
                onFewShotChange={onFewShotChange}
                onRemoveFewShot={onRemoveFewShot}
              />
            ))}
            {fewShots.length === 0 && (
              <p className='py-3 text-center text-xs text-gray-400'>
                No few-shot examples. Click 'Add Example' to create one.
              </p>
            )}
          </div>
        </div>
        <Separator />
        <div>
          <Label htmlFor='user-input' className='mb-1 block text-xs font-medium text-gray-700'>
            User Input (Final Prompt)
          </Label>
          <Textarea
            id='user-input'
            value={userInput}
            onChange={e => onUserInputchange(e.target.value)}
            placeholder='Enter your final prompt here for the AI to process...'
            className='min-h-[120px] resize-none rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500'
            rows={5}
          />
        </div>
        <div className='mt-4 flex items-center gap-2'>
          <Button
            onClick={onTest}
            className='bg-green-600 py-2 text-sm text-white hover:bg-green-700'
            disabled={isTestDisabled}
          >
            <Send className='mr-1.5 h-3.5 w-3.5' />
            Test Prompt
          </Button>
          <Button
            variant='outline'
            onClick={onOpenVariablesDialog}
            disabled={variableKeysCount === 0}
            className='py-2 text-sm'
          >
            Edit Variables ({variableKeysCount})
          </Button>
        </div>
      </div>
    </div>
  );
};

export default PromptEditor;
