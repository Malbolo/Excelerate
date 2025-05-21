import { ArrowLeftIcon, ArrowUpToLine } from 'lucide-react';

import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import useInternalRouter from '@/hooks/useInternalRouter';

interface PlaygroundHeaderProps {
  llmCategories: string[];
  selectedCategory?: string;
  onCategoryChange: (value: string) => void;
  availableFeatures: string[];
  selectedFeature?: string;
  onFeatureChange: (value: string) => void;
  onSubmitParameters: () => void;
  isSubmitDisabled: boolean;
}

const PlaygroundHeader = ({
  llmCategories,
  selectedCategory,
  onCategoryChange,
  availableFeatures,
  selectedFeature,
  onFeatureChange,
  onSubmitParameters,
  isSubmitDisabled,
}: PlaygroundHeaderProps) => {
  const { goBack } = useInternalRouter();
  return (
    <header className='sticky top-1.5 z-10 flex h-14 items-center justify-between px-4'>
      <div className='flex items-center gap-3'>
        <Button variant='ghost' size='sm' onClick={() => goBack()} className='flex items-center gap-1.5'>
          <ArrowLeftIcon className='h-4 w-4' />
          Back
        </Button>
        <h1 className='text-lg font-bold'>LLM Playground</h1>
      </div>
      <div className='flex items-center gap-2.5'>
        <Select value={selectedCategory} onValueChange={onCategoryChange}>
          <SelectTrigger className='w-[180px] bg-white text-xs'>
            <SelectValue placeholder='Select Category' />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel className='text-xs'>Categories</SelectLabel>
              {llmCategories.map(cat => (
                <SelectItem key={cat} value={cat} className='text-xs'>
                  {cat}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <Select
          value={selectedFeature}
          onValueChange={onFeatureChange}
          disabled={!selectedCategory || availableFeatures.length === 0}
        >
          <SelectTrigger className='w-[200px] bg-white text-xs'>
            <SelectValue placeholder='Select Feature' />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel className='text-xs'>Features</SelectLabel>
              {availableFeatures.map(feat => (
                <SelectItem key={feat} value={feat} className='text-xs'>
                  {feat}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <Button onClick={onSubmitParameters} size='sm' disabled={isSubmitDisabled}>
          <ArrowUpToLine className='h-4 w-4' />
          Load Template
        </Button>
      </div>
    </header>
  );
};

export default PlaygroundHeader;
