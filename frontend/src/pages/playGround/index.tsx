import { useEffect, useState } from 'react';

import { ArrowLeftIcon, PlusIcon, Send, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

import {
  useGetLLMTemplate,
  useGetLLMTemplateByCategory,
} from '@/apis/playground';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import useInternalRouter from '@/hooks/useInternalRouter';

interface FewShot {
  id: string;
  userPrompt: string;
  aiPrompt: string;
}

const LLMPlaygroundPage = () => {
  const { goBack } = useInternalRouter();

  const { data: llmTemplate } = useGetLLMTemplate();
  const getLLMTemplateByCategory = useGetLLMTemplateByCategory();

  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(
    undefined,
  );
  const [availableFeatures, setAvailableFeatures] = useState<string[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<string | undefined>(
    undefined,
  );

  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [fewShots, setFewShots] = useState<FewShot[]>([
    { id: '1', userPrompt: '', aiPrompt: '' },
  ]);
  const [userInput, setUserInput] = useState<string>('');

  useEffect(() => {
    if (selectedCategory) {
      setAvailableFeatures(llmTemplate[selectedCategory] || []);
      setSelectedFeature(undefined);
    } else {
      setAvailableFeatures([]);
      setSelectedFeature(undefined);
    }
  }, [selectedCategory]);

  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value);
  };

  const handleFeatureChange = (value: string) => {
    setSelectedFeature(value);
  };

  const handleSubmitParameters = async () => {
    if (!selectedCategory || !selectedFeature) {
      toast.error('Please select both a category and a feature.');
      return;
    }

    const result = await getLLMTemplateByCategory({
      agent: selectedCategory,
      template_name: selectedFeature,
    });
    console.log('Result:', result);
  };

  const addFewShot = () => {
    if (fewShots.length >= 5) {
      toast.error('You can only add up to 5 few-shots.');
      return;
    }
    setFewShots(prev => [
      ...prev,
      { id: `${prev.length + 1}`, userPrompt: '', aiPrompt: '' },
    ]);
  };

  const removeFewShot = (idToRemove: string) => {
    setFewShots(fewShots.filter(fs => fs.id !== idToRemove));
  };

  const handleFewShotChange = (
    id: string,
    field: 'userPrompt' | 'aiPrompt',
    value: string,
  ) => {
    setFewShots(
      fewShots.map(fs => (fs.id === id ? { ...fs, [field]: value } : fs)),
    );
  };

  const handleTest = () => {
    const payload = {
      systemPrompt,
      fewShots,
      userInput,
    };
    console.log('Test Payload (JSON):', JSON.stringify(payload, null, 2));
    toast.success('Test payload logged to console!');
  };

  return (
    <section className='flex h-screen flex-1 flex-col bg-gray-100'>
      <header className='sticky top-0 z-10 flex h-14 items-center justify-between border-b bg-white px-4 shadow-sm'>
        <div className='flex items-center gap-3'>
          <Button
            variant='ghost'
            size='sm'
            onClick={goBack}
            className='flex items-center gap-1.5 text-gray-700 hover:bg-gray-200'
          >
            <ArrowLeftIcon className='h-4 w-4' />
            Back
          </Button>
          <h1 className='text-md font-semibold text-gray-800'>
            LLM Playground
          </h1>
        </div>
        <div className='flex items-center gap-2.5'>
          <Select value={selectedCategory} onValueChange={handleCategoryChange}>
            <SelectTrigger className='w-[180px] bg-white text-xs'>
              <SelectValue placeholder='Select Category' />
            </SelectTrigger>
            <SelectContent>
              <SelectGroup>
                <SelectLabel className='text-xs'>Categories</SelectLabel>
                {Object.keys(llmTemplate).map(cat => (
                  <SelectItem key={cat} value={cat} className='text-xs'>
                    {cat}
                  </SelectItem>
                ))}
              </SelectGroup>
            </SelectContent>
          </Select>
          <Select
            value={selectedFeature}
            onValueChange={handleFeatureChange}
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
          <Button
            onClick={handleSubmitParameters}
            size='sm'
            className='bg-blue-600 text-white hover:bg-blue-700'
            disabled={!selectedCategory || !selectedFeature}
          >
            <Send className='mr-1.5 h-4 w-4' />
            Submit
          </Button>
        </div>
      </header>

      <div className='flex flex-1 gap-3 overflow-hidden p-3'>
        <div className='w-3/5 overflow-y-auto rounded-lg border bg-white p-0.5 shadow-sm xl:w-2/3'>
          <div className='space-y-5 p-4'>
            <div>
              <Label
                htmlFor='system-prompt'
                className='mb-1 block text-xs font-medium text-gray-700'
              >
                System Prompt
              </Label>
              <Textarea
                id='system-prompt'
                value={systemPrompt}
                onChange={e => setSystemPrompt(e.target.value)}
                placeholder='Define the AI behavior and context here...'
                className='min-h-[100px] resize-none rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500'
                rows={4}
              />
            </div>
            <Separator />
            <div>
              <div className='mb-2.5 flex items-center justify-between'>
                <h3 className='text-xs font-medium text-gray-700'>
                  Few-shot Prompts
                </h3>
                <Button
                  variant='outline'
                  size='sm'
                  onClick={addFewShot}
                  className='flex items-center gap-1 border-blue-500 py-1 text-xs text-blue-600 hover:bg-blue-50 hover:text-blue-700' // gap-1.5->gap-1, text-xs 추가, py-1 추가
                >
                  <PlusIcon className='h-3.5 w-3.5' />
                  Add
                </Button>
              </div>
              <div className='space-y-3'>
                {fewShots.map((fs, index) => (
                  <div
                    key={fs.id}
                    className='rounded-md border border-gray-200 bg-gray-50/50 p-3' // p-4->p-3
                  >
                    <div className='mb-2 flex items-center justify-between'>
                      <span className='text-xs font-semibold text-gray-600'>
                        Example {index + 1}
                      </span>
                      {fewShots.length > 0 && (
                        <Button
                          variant='ghost'
                          size='icon'
                          onClick={() => removeFewShot(fs.id)}
                          className='h-6 w-6 text-red-500 hover:bg-red-100 hover:text-red-600' // h-7 w-7 -> h-6 w-6
                          aria-label='Remove few-shot'
                        >
                          <Trash2 className='h-3.5 w-3.5' />
                        </Button>
                      )}
                    </div>
                    <div className='space-y-2.5'>
                      <div>
                        <Label
                          htmlFor={`fs-user-${fs.id}`}
                          className='mb-0.5 block text-xs font-medium text-gray-700' // mb-1->mb-0.5
                        >
                          User Prompt
                        </Label>
                        <Textarea
                          id={`fs-user-${fs.id}`}
                          value={fs.userPrompt}
                          onChange={e =>
                            handleFewShotChange(
                              fs.id,
                              'userPrompt',
                              e.target.value,
                            )
                          }
                          placeholder='User says...'
                          className='min-h-[70px] resize-none rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500'
                          rows={3}
                        />
                      </div>
                      <div>
                        <Label
                          htmlFor={`fs-ai-${fs.id}`}
                          className='mb-0.5 block text-xs font-medium text-gray-700' // mb-1->mb-0.5
                        >
                          AI Prompt (Assistant's Response)
                        </Label>
                        <Textarea
                          id={`fs-ai-${fs.id}`}
                          value={fs.aiPrompt}
                          onChange={e =>
                            handleFewShotChange(
                              fs.id,
                              'aiPrompt',
                              e.target.value,
                            )
                          }
                          placeholder='AI responds...'
                          className='min-h-[70px] resize-none rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500'
                          rows={3}
                        />
                      </div>
                    </div>
                  </div>
                ))}
                {fewShots.length === 0 && (
                  <p className='py-3 text-center text-xs text-gray-400'>
                    No few-shot examples. Click 'Add' to create one.
                  </p>
                )}
              </div>
            </div>
            <Separator />
            <div>
              <Label
                htmlFor='user-input'
                className='mb-1 block text-xs font-medium text-gray-700'
              >
                User Input
              </Label>
              <Textarea
                id='user-input'
                value={userInput}
                onChange={e => setUserInput(e.target.value)}
                placeholder='Enter your final prompt here for the AI to process...'
                className='min-h-[120px] resize-none rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500'
                rows={5}
              />
            </div>
            <Button
              onClick={handleTest}
              className='bg-green-600 py-2 text-sm text-white hover:bg-green-700'
            >
              Test
            </Button>
          </div>
        </div>
        <div className='flex w-2/5 flex-col gap-3 xl:w-1/3'>
          <Card className='flex-1'>
            <CardHeader className='p-3'>
              <CardTitle className='text-sm font-semibold text-gray-700'>
                Original AI Output
              </CardTitle>
            </CardHeader>
            <CardContent className='p-3 text-xs text-gray-600'>
              <p className='italic'>
                AI output based on initial parameters will appear here.
              </p>
            </CardContent>
          </Card>
          <Card className='flex-1'>
            <CardHeader className='p-3'>
              <CardTitle className='text-sm font-semibold text-gray-700'>
                Modified AI Output
              </CardTitle>
            </CardHeader>
            <CardContent className='p-3 text-xs text-gray-600'>
              <p className='italic'>
                AI output based on your modified prompts will appear here.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
};

export default LLMPlaygroundPage;
