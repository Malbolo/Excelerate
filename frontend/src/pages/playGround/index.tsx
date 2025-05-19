import { useEffect, useMemo, useState } from 'react';

import { toast } from 'sonner';

import {
  useGetLLMTemplate,
  useGetLLMTemplateByCategory,
  usePostCallPrompt,
  usePostTemplatePrompt,
} from '@/apis/playground';

import OutputDisplay from './components/OutputDisplay';
import PlaygroundHeader from './components/PlaygroundHeader';
import PromptEditor from './components/PromptEditor';
import VariablesEditorDialog from './components/VariablesEditorDialog';

interface FewShot {
  human: string;
  ai: string;
  index: number;
}

const LLMPlaygroundPage = () => {
  const { data: llmTemplateData } = useGetLLMTemplate();
  const getLLMTemplateByCategory = useGetLLMTemplateByCategory();
  const postCallPrompt = usePostCallPrompt();
  const postTemplatePrompt = usePostTemplatePrompt();

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

  const [selectedVariableKeyInDialog, setSelectedVariableKeyInDialog] = useState<string | null>(null);

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
      setTemplateOutput('');
      setTemplateName('');
    } else {
      setAvailableFeatures([]);
      setSelectedFeature(undefined);
    }
  }, [selectedCategory, llmTemplateData]);

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
    setTemplateOutput('');
    setTemplateName('');
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
    setSystemPrompt(result.system || '');
    setFewShots(
      result.fewshot ? result.fewshot.map((fs, index) => ({ ...fs, index })) : [{ human: '', ai: '', index: 0 }],
    );
    setUserInput(result.human || '');
    setVariables(result.variables || {});
    setTemplateName(result.template_name || '');
    setModifiedOutput('');
    setTemplateOutput('');
    toast.success('Template loaded successfully!');
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

  const handleFewShotChange = (internalIndex: number, field: 'human' | 'ai', value: string) => {
    setFewShots(fewShots.map(fs => (fs.index === internalIndex ? { ...fs, [field]: value } : fs)));
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
    const commonPayload = {
      systemPrompt: systemPrompt,
      fewShots: fewShots.map(({ index, ...rest }) => rest),
      userInput: userInput,
      variables: variables,
    };
    toast.info('Sending prompt to AI...');
    const callResult = await postCallPrompt(commonPayload);
    setModifiedOutput(callResult.output || 'No output received.');
    toast.success('AI response (direct call) received!');

    if (selectedCategory && templateName) {
      const templatePayload = {
        template_name: `${selectedCategory}:${templateName}`,
        variables: variables,
      };
      const templateCallResult = await postTemplatePrompt(templatePayload);
      setTemplateOutput(templateCallResult.output || 'No template output received.');
      toast.success('AI response (template call) received!');
    } else {
      setTemplateOutput('Template name not available for template call.');
    }
  };

  const currentVariableKeys = Object.keys(variables);
  const isTestButtonDisabled = !systemPrompt && fewShots.every(fs => !fs.human && !fs.ai) && !userInput;

  return (
    <section className='flex h-screen flex-1 flex-col bg-gray-100'>
      <PlaygroundHeader
        llmCategories={llmCategories}
        selectedCategory={selectedCategory}
        onCategoryChange={handleCategoryChange}
        availableFeatures={availableFeatures}
        selectedFeature={selectedFeature}
        onFeatureChange={handleFeatureChange}
        onSubmitParameters={handleSubmitParameters}
        isSubmitDisabled={!selectedCategory || !selectedFeature}
      />

      <div className='flex flex-1 gap-3 overflow-hidden p-3'>
        <PromptEditor
          systemPrompt={systemPrompt}
          onSystemPromptChange={setSystemPrompt}
          fewShots={fewShots}
          onAddFewShot={addFewShot}
          onRemoveFewShot={removeFewShot}
          onFewShotChange={handleFewShotChange}
          userInput={userInput}
          onUserInputchange={setUserInput}
          onTest={handleTest}
          onOpenVariablesDialog={() => setIsVariablesDialogOpen(true)}
          variableKeysCount={currentVariableKeys.length}
          isTestDisabled={isTestButtonDisabled}
        />
        <OutputDisplay templateOutput={templateOutput} modifiedOutput={modifiedOutput} />
      </div>

      <VariablesEditorDialog
        isOpen={isVariablesDialogOpen}
        onOpenChange={setIsVariablesDialogOpen}
        variables={variables}
        onVariableChange={handleVariableChange}
        selectedVariableKey={selectedVariableKeyInDialog}
        onSetSelectedVariableKey={setSelectedVariableKeyInDialog}
      />
    </section>
  );
};

export default LLMPlaygroundPage;
