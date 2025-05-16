import { useEffect, useMemo, useState } from 'react';

import { ArrowLeftIcon, PlusIcon, Send, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

import {
  useGetLLMTemplate,
  useGetLLMTemplateByCategory,
  usePostCallPrompt,
} from '@/apis/playground';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
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
  human: string;
  ai: string;
  index: number;
}

const LLMPlaygroundPage = () => {
  const { goBack } = useInternalRouter();

  const { data: llmTemplate } = useGetLLMTemplate();
  const getLLMTemplateByCategory = useGetLLMTemplateByCategory();
  const postCallPrompt = usePostCallPrompt();

  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(
    undefined,
  );
  const [availableFeatures, setAvailableFeatures] = useState<string[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<string | undefined>(
    undefined,
  );
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [fewShots, setFewShots] = useState<FewShot[]>([
    { human: '', ai: '', index: 0 },
  ]);
  const [userInput, setUserInput] = useState<string>('');
  const [variables, setVariables] = useState<{ [key: string]: string }>({});
  const [isVariablesDialogOpen, setIsVariablesDialogOpen] = useState(false);
  const [output, setOutput] = useState<string>('');
  const [modifiedOutput, setModifiedOutput] = useState<string>('');

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

    setSystemPrompt(result.system);
    setFewShots(result.fewshot.map((fs, index) => ({ ...fs, index })));
    setUserInput(result.human);
  };

  const addFewShot = () => {
    if (fewShots.length >= 5) {
      toast.error('You can only add up to 5 few-shots.');
      return;
    }
    setFewShots(prev => [...prev, { human: '', ai: '', index: prev.length }]);
  };

  const removeFewShot = (idToRemove: number) => {
    setFewShots(fewShots.filter(fs => fs.index !== idToRemove));
  };

  const handleFewShotChange = (
    index: number,
    field: 'human' | 'ai',
    value: string,
  ) => {
    setFewShots(
      fewShots.map(fs => (fs.index === index ? { ...fs, [field]: value } : fs)),
    );
  };

  const extractedVariableKeys = useMemo(() => {
    const allText = [
      systemPrompt,
      ...fewShots.flatMap(fs => [fs.human, fs.ai]),
      userInput,
    ].join(' ');

    const regex = /\{([^}]+)\}/g;
    const matches = new Set<string>();
    let match;
    while ((match = regex.exec(allText)) !== null) {
      matches.add(match[1]);
    }
    return Array.from(matches);
  }, [systemPrompt, fewShots, userInput]);

  useEffect(() => {
    const newVariables = { ...variables };
    let updated = false;
    extractedVariableKeys.forEach(key => {
      if (!(key in newVariables)) {
        newVariables[key] = ''; // Initialize new variables with empty string
        updated = true;
      }
    });
    Object.keys(newVariables).forEach(key => {
      if (!extractedVariableKeys.includes(key)) {
        delete newVariables[key];
        updated = true;
      }
    });
    if (updated) {
      setVariables(newVariables);
    }
  }, [extractedVariableKeys]);

  const handleVariableChange = (key: string, value: string) => {
    setVariables(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleTest = async () => {
    const payload = {
      systemPrompt,
      fewShots,
      userInput,
      variables,
    };
    toast.success('Test payload logged to console!');
    const result = await postCallPrompt(payload);
    setModifiedOutput(result.output);
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
                  className='flex items-center gap-1 border-blue-500 py-1 text-xs text-blue-600 hover:bg-blue-50 hover:text-blue-700'
                >
                  <PlusIcon className='h-3.5 w-3.5' />
                  Add
                </Button>
              </div>
              <div className='space-y-3'>
                {fewShots.map((fs, index) => (
                  <div
                    key={fs.index}
                    className='rounded-md border border-gray-200 bg-gray-50/50 p-3'
                  >
                    <div className='mb-2 flex items-center justify-between'>
                      <span className='text-xs font-semibold text-gray-600'>
                        Example {index + 1}
                      </span>
                      {fewShots.length > 0 && (
                        <Button
                          variant='ghost'
                          size='icon'
                          onClick={() => removeFewShot(fs.index)}
                          className='h-6 w-6 text-red-500 hover:bg-red-100 hover:text-red-600'
                          aria-label='Remove few-shot'
                        >
                          <Trash2 className='h-3.5 w-3.5' />
                        </Button>
                      )}
                    </div>
                    <div className='space-y-2.5'>
                      <div>
                        <Label
                          htmlFor={`fs-user-${fs.index}`}
                          className='mb-0.5 block text-xs font-medium text-gray-700'
                        >
                          User Prompt
                        </Label>
                        <Textarea
                          id={`fs-user-${fs.index}`}
                          value={fs.human}
                          onChange={e =>
                            handleFewShotChange(
                              fs.index,
                              'human',
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
                          htmlFor={`fs-ai-${fs.index}`}
                          className='mb-0.5 block text-xs font-medium text-gray-700'
                        >
                          AI Prompt (Assistant's Response)
                        </Label>
                        <Textarea
                          id={`fs-ai-${fs.index}`}
                          value={fs.ai}
                          onChange={e =>
                            handleFewShotChange(fs.index, 'ai', e.target.value)
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
            <div className='mt-4 flex items-center gap-2'>
              <Button
                onClick={handleTest}
                className='bg-green-600 py-2 text-sm text-white hover:bg-green-700'
              >
                Test
              </Button>
              <Button
                variant='outline'
                onClick={() => setIsVariablesDialogOpen(true)}
                disabled={extractedVariableKeys.length === 0}
                className='py-2 text-sm'
              >
                Edit Variables ({extractedVariableKeys.length})
              </Button>
            </div>
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

      <Dialog
        open={isVariablesDialogOpen}
        onOpenChange={setIsVariablesDialogOpen}
      >
        <DialogContent className='sm:max-w-[500px]'>
          <DialogHeader>
            <DialogTitle>Edit Variables</DialogTitle>
            <DialogDescription>
              Set the values for the variables found in your prompts. Click Done
              when you're finished.
            </DialogDescription>
          </DialogHeader>
          <div className='grid gap-4 py-4'>
            {extractedVariableKeys.length > 0 ? (
              extractedVariableKeys.map(key => (
                <div className='grid grid-cols-4 items-center gap-4' key={key}>
                  <Label
                    htmlFor={`variable-dialog-${key}`}
                    className='text-right'
                  >
                    {key}
                  </Label>
                  <Input
                    id={`variable-dialog-${key}`}
                    value={variables[key] || ''}
                    onChange={e => handleVariableChange(key, e.target.value)}
                    className='col-span-3'
                    placeholder={`Value for {${key}}`}
                  />
                </div>
              ))
            ) : (
              <p className='col-span-4 py-4 text-center text-sm text-gray-500'>
                No variables found in the prompts.
              </p>
            )}
          </div>
          <DialogFooter>
            <Button
              type='button'
              onClick={() => setIsVariablesDialogOpen(false)}
            >
              Done
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
};

export default LLMPlaygroundPage;
