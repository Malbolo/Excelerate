import { useEffect, useRef, useState } from 'react';
import { useMemo } from 'react';

// useRef 추가

import { ArrowLeftIcon, PlusIcon, Send, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

import {
  useGetLLMTemplate,
  useGetLLMTemplateByCategory,
  usePostCallPrompt,
  usePostTemplatePrompt,
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

  const { data: llmTemplateData } = useGetLLMTemplate();
  const getLLMTemplateByCategory = useGetLLMTemplateByCategory();
  const postCallPrompt = usePostCallPrompt();

  const [selectedCategory, setSelectedCategory] = useState<string | undefined>(undefined);
  const [availableFeatures, setAvailableFeatures] = useState<string[]>([]);
  const [selectedFeature, setSelectedFeature] = useState<string | undefined>(undefined);
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [fewShots, setFewShots] = useState<FewShot[]>([{ human: '', ai: '', index: 0 }]);
  const [userInput, setUserInput] = useState<string>('');
  const [variables, setVariables] = useState<{ [key: string]: string }>({});
  const [isVariablesDialogOpen, setIsVariablesDialogOpen] = useState(false);
  const [modifiedOutput, setModifiedOutput] = useState<string>('');
  const [templateOutput, setTemplateOutput] = useState<string>('');
  const [templateName, setTemplateName] = useState('');
  const postTemplatePrompt = usePostTemplatePrompt();

  const [selectedVariableKeyInDialog, setSelectedVariableKeyInDialog] = useState<string | null>(null);
  const variableValueTextareaRef = useRef<HTMLTextAreaElement>(null);

  const llmCategories = useMemo(() => {
    return llmTemplateData ? Object.keys(llmTemplateData) : [];
  }, [llmTemplateData]);

  useEffect(() => {
    if (selectedCategory && llmTemplateData) {
      setAvailableFeatures(llmTemplateData[selectedCategory] || []);
      setSelectedFeature(undefined);
      setSystemPrompt('');
      setFewShots([{ human: '', ai: '', index: 0 }]);
      setUserInput('');
      setVariables({});
      setModifiedOutput('');
    } else {
      setAvailableFeatures([]);
      setSelectedFeature(undefined);
    }
  }, [selectedCategory, llmTemplateData]);

  useEffect(() => {
    if (isVariablesDialogOpen) {
      const currentKeys = Object.keys(variables);
      if (currentKeys.length > 0) {
        if (!selectedVariableKeyInDialog || !variables.hasOwnProperty(selectedVariableKeyInDialog)) {
          setSelectedVariableKeyInDialog(currentKeys[0]);
        }
      } else {
        setSelectedVariableKeyInDialog(null);
      }
    }
  }, [isVariablesDialogOpen, variables]);

  useEffect(() => {
    if (selectedVariableKeyInDialog && variableValueTextareaRef.current) {
      variableValueTextareaRef.current.focus();
    }
  }, [selectedVariableKeyInDialog]);

  const handleCategoryChange = (value: string) => {
    setSelectedCategory(value);
  };

  const handleFeatureChange = (value: string) => {
    setSelectedFeature(value);
    setSystemPrompt('');
    setFewShots([{ human: '', ai: '', index: 0 }]);
    setUserInput('');
    setVariables({});
    setModifiedOutput('');
  };

  const handleSubmitParameters = async () => {
    if (!selectedCategory || !selectedFeature) {
      toast.error('Please select both a category and a feature.');
      return;
    }

    const { system, fewshot, human, variables, template_name } = await getLLMTemplateByCategory({
      agent: selectedCategory,
      template_name: selectedFeature,
    });

    setSystemPrompt(system || '');
    setFewShots(fewshot ? fewshot.map((fs, index) => ({ ...fs, index })) : [{ human: '', ai: '', index: 0 }]);
    setUserInput(human || '');
    setVariables(variables || {});
    setModifiedOutput('');
    setTemplateName(template_name || '');
  };

  const addFewShot = () => {
    if (fewShots.length >= 5) {
      toast.error('You can only add up to 5 few-shots.');
      return;
    }
    setFewShots(prev => [
      ...prev,
      { human: '', ai: '', index: prev.length > 0 ? Math.max(...prev.map(fs => fs.index)) + 1 : 0 },
    ]);
  };

  const removeFewShot = (indexToRemove: number) => {
    setFewShots(fewShots.filter(fs => fs.index !== indexToRemove));
  };

  const handleFewShotChange = (index: number, field: 'human' | 'ai', value: string) => {
    setFewShots(fewShots.map(fs => (fs.index === index ? { ...fs, [field]: value } : fs)));
  };

  const handleVariableChange = (key: string, value: string) => {
    setVariables(prev => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleTest = async () => {
    if (!systemPrompt && fewShots.every(fs => !fs.human && !fs.ai) && !userInput) {
      toast.error('Please provide some input (System Prompt, Few-shots, or User Input) to test.');
      return;
    }
    const payload = {
      systemPrompt: systemPrompt,
      fewShots: fewShots.map(({ index, ...rest }) => rest),
      userInput: userInput,
      variables: variables,
    };

    const result = await postCallPrompt(payload);
    const templateResult = await postTemplatePrompt({
      template_name: `${selectedCategory}:${templateName}`,
      variables: variables,
    });
    setModifiedOutput(result.output || 'No output received.');
    setTemplateOutput(templateResult.output || 'No output received.');
  };

  const currentVariableKeys = Object.keys(variables);

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
          <h1 className='text-md font-semibold text-gray-800'>LLM Playground</h1>
        </div>
        <div className='flex items-center gap-2.5'>
          <Select value={selectedCategory} onValueChange={handleCategoryChange}>
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
            Load Template
          </Button>
        </div>
      </header>

      <div className='flex flex-1 gap-3 overflow-hidden p-3'>
        <div className='w-3/5 overflow-y-auto rounded-lg border bg-white p-0.5 shadow-sm xl:w-2/3'>
          <div className='space-y-5 p-4'>
            <div>
              <Label htmlFor='system-prompt' className='mb-1 block text-xs font-medium text-gray-700'>
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
                <h3 className='text-xs font-medium text-gray-700'>Few-shot Prompts (Examples)</h3>
                <Button
                  variant='outline'
                  size='sm'
                  onClick={addFewShot}
                  className='flex items-center gap-1 border-blue-500 py-1 text-xs text-blue-600 hover:bg-blue-50 hover:text-blue-700'
                >
                  <PlusIcon className='h-3.5 w-3.5' />
                  Add Example
                </Button>
              </div>
              <div className='space-y-3'>
                {fewShots.map((fs, index) => (
                  <div key={fs.index} className='rounded-md border border-gray-200 bg-gray-50/50 p-3'>
                    <div className='mb-2 flex items-center justify-between'>
                      <span className='text-xs font-semibold text-gray-600'>Example {index + 1}</span>
                      <Button
                        variant='ghost'
                        size='icon'
                        onClick={() => removeFewShot(fs.index)}
                        className='h-6 w-6 text-red-500 hover:bg-red-100 hover:text-red-600'
                        aria-label='Remove few-shot'
                      >
                        <Trash2 className='h-3.5 w-3.5' />
                      </Button>
                    </div>
                    <div className='space-y-2.5'>
                      <div>
                        <Label
                          htmlFor={`fs-user-${fs.index}`}
                          className='mb-0.5 block text-xs font-medium text-gray-700'
                        >
                          User Input (Example)
                        </Label>
                        <Textarea
                          id={`fs-user-${fs.index}`}
                          value={fs.human}
                          onChange={e => handleFewShotChange(fs.index, 'human', e.target.value)}
                          placeholder='User says...'
                          className='min-h-[70px] resize-none rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500'
                          rows={3}
                        />
                      </div>
                      <div>
                        <Label htmlFor={`fs-ai-${fs.index}`} className='mb-0.5 block text-xs font-medium text-gray-700'>
                          AI Response (Example)
                        </Label>
                        <Textarea
                          id={`fs-ai-${fs.index}`}
                          value={fs.ai}
                          onChange={e => handleFewShotChange(fs.index, 'ai', e.target.value)}
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
                onChange={e => setUserInput(e.target.value)}
                placeholder='Enter your final prompt here for the AI to process...'
                className='min-h-[120px] resize-none rounded-md border-gray-300 text-sm focus:border-blue-500 focus:ring-blue-500'
                rows={5}
              />
            </div>
            <div className='mt-4 flex items-center gap-2'>
              <Button onClick={handleTest} className='bg-green-600 py-2 text-sm text-white hover:bg-green-700'>
                <Send className='mr-1.5 h-3.5 w-3.5' />
                Test Prompt
              </Button>
              <Button
                variant='outline'
                onClick={() => setIsVariablesDialogOpen(true)}
                disabled={currentVariableKeys.length === 0}
                className='py-2 text-sm'
              >
                Edit Variables ({currentVariableKeys.length})
              </Button>
            </div>
          </div>
        </div>
        <div className='flex w-2/5 flex-col gap-3 overflow-y-auto xl:w-1/3'>
          <Card className='flex-1'>
            <CardHeader className='p-3'>
              <CardTitle className='text-sm font-semibold text-gray-700'>Original AI Output</CardTitle>
            </CardHeader>
            <CardContent className='flex-1 overflow-y-auto p-3 text-xs whitespace-pre-wrap text-gray-600'>
              {templateOutput ? templateOutput : <p className='italic'>AI output will appear here after testing.</p>}
            </CardContent>
          </Card>

          <Card className='flex flex-1 flex-col'>
            <CardHeader className='p-3'>
              <CardTitle className='text-sm font-semibold text-gray-700'>AI Output</CardTitle>
            </CardHeader>
            <CardContent className='flex-1 overflow-y-auto p-3 text-xs whitespace-pre-wrap text-gray-600'>
              {modifiedOutput ? modifiedOutput : <p className='italic'>AI output will appear here after testing.</p>}
            </CardContent>
          </Card>
        </div>
      </div>

      <Dialog
        open={isVariablesDialogOpen}
        onOpenChange={open => {
          setIsVariablesDialogOpen(open);
          if (!open) {
            setSelectedVariableKeyInDialog(null);
          }
        }}
      >
        <DialogContent className='flex h-[70vh] max-w-lg flex-col p-0 sm:max-w-xl md:h-[75vh] md:max-w-2xl lg:max-w-3xl'>
          <DialogHeader className='p-6 pb-4'>
            <DialogTitle>Edit Variables</DialogTitle>
            <DialogDescription>
              Select a variable on the left to edit its value. These are pre-filled with default values. Click Done when
              you're finished.
            </DialogDescription>
          </DialogHeader>

          <div className='flex flex-1 gap-0 overflow-hidden border-t'>
            <div className='w-1/3 overflow-y-auto border-r bg-slate-50/50 p-3'>
              <h4 className='sticky top-0 -mx-3 mb-2 border-b bg-slate-50/50 px-3 py-1.5 text-xs font-semibold text-slate-600'>
                VARIABLES ({currentVariableKeys.length})
              </h4>
              <div className='space-y-1'>
                {currentVariableKeys.length > 0 ? (
                  currentVariableKeys.map(key => (
                    <Button
                      key={key}
                      variant={'ghost'}
                      onClick={() => setSelectedVariableKeyInDialog(key)}
                      className={`h-auto w-full justify-start truncate rounded-md px-2 py-1.5 text-left text-sm transition-colors duration-100 ease-in-out ${
                        selectedVariableKeyInDialog === key
                          ? 'bg-blue-100 font-medium text-blue-700'
                          : 'text-slate-700 hover:bg-slate-200/60'
                      }`}
                    >
                      {key}
                    </Button>
                  ))
                ) : (
                  <p className='px-1 py-2 text-xs text-slate-500 italic'>No variables loaded.</p>
                )}
              </div>
            </div>

            <div className='flex w-2/3 flex-col space-y-2 bg-white p-4'>
              {selectedVariableKeyInDialog && variables.hasOwnProperty(selectedVariableKeyInDialog) ? (
                <>
                  <Label
                    htmlFor={`variable-dialog-value-${selectedVariableKeyInDialog}`}
                    className='text-sm font-medium text-slate-800'
                  >
                    Editing: <span className='font-semibold text-blue-600'>{selectedVariableKeyInDialog}</span>
                  </Label>
                  <Textarea
                    ref={variableValueTextareaRef}
                    id={`variable-dialog-value-${selectedVariableKeyInDialog}`}
                    value={variables[selectedVariableKeyInDialog] || ''}
                    onChange={e => handleVariableChange(selectedVariableKeyInDialog, e.target.value)}
                    className='flex-1 resize-none rounded-md border-slate-300 p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500'
                    placeholder={`Enter value for {${selectedVariableKeyInDialog}}...`}
                    rows={10}
                  />
                  <p className='text-xs text-slate-500'>
                    The value for this variable will be used when testing the prompt.
                  </p>
                </>
              ) : (
                <div className='flex flex-1 items-center justify-center text-center'>
                  <p className='text-sm text-slate-500'>
                    {currentVariableKeys.length > 0
                      ? 'Select a variable on the left to edit its value.'
                      : 'No variables available for this template or template not loaded yet.'}
                  </p>
                </div>
              )}
            </div>
          </div>
          <DialogFooter className='border-t p-6 pt-4'>
            <Button
              type='button'
              onClick={() => setIsVariablesDialogOpen(false)}
              className='bg-blue-600 text-white hover:bg-blue-700'
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
