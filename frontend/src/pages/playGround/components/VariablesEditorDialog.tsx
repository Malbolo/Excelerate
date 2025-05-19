import { useEffect, useRef } from 'react';

import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';

interface VariablesEditorDialogProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  variables: { [key: string]: string };
  onVariableChange: (key: string, value: string) => void;
  selectedVariableKey: string | null;
  onSetSelectedVariableKey: (key: string | null) => void;
}

const VariablesEditorDialog = ({
  isOpen,
  onOpenChange,
  variables,
  onVariableChange,
  selectedVariableKey,
  onSetSelectedVariableKey,
}: VariablesEditorDialogProps) => {
  const variableValueTextareaRef = useRef<HTMLTextAreaElement>(null);
  const currentVariableKeys = Object.keys(variables);

  useEffect(() => {
    if (isOpen) {
      if (currentVariableKeys.length > 0) {
        if (!selectedVariableKey || !variables.hasOwnProperty(selectedVariableKey)) {
          onSetSelectedVariableKey(currentVariableKeys[0]);
        }
      } else {
        onSetSelectedVariableKey(null);
      }
    }
  }, [isOpen, variables, selectedVariableKey, onSetSelectedVariableKey, currentVariableKeys]);

  useEffect(() => {
    if (selectedVariableKey && variableValueTextareaRef.current) {
      variableValueTextareaRef.current.focus();
    }
  }, [selectedVariableKey]);

  return (
    <Dialog
      open={isOpen}
      onOpenChange={open => {
        onOpenChange(open);
        if (!open) {
          onSetSelectedVariableKey(null);
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
                    onClick={() => onSetSelectedVariableKey(key)}
                    className={`h-auto w-full justify-start truncate rounded-md px-2 py-1.5 text-left text-sm transition-colors duration-100 ease-in-out ${
                      selectedVariableKey === key
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
            {selectedVariableKey && variables.hasOwnProperty(selectedVariableKey) ? (
              <>
                <Label
                  htmlFor={`variable-dialog-value-${selectedVariableKey}`}
                  className='text-sm font-medium text-slate-800'
                >
                  Editing: <span className='font-semibold text-blue-600'>{selectedVariableKey}</span>
                </Label>
                <Textarea
                  ref={variableValueTextareaRef}
                  id={`variable-dialog-value-${selectedVariableKey}`}
                  value={variables[selectedVariableKey] || ''}
                  onChange={e => onVariableChange(selectedVariableKey, e.target.value)}
                  className='flex-1 resize-none rounded-md border-slate-300 p-2.5 text-sm shadow-sm focus:border-blue-500 focus:ring-blue-500'
                  placeholder={`Enter value for {${selectedVariableKey}}...`}
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
            onClick={() => onOpenChange(false)}
            className='bg-blue-600 text-white hover:bg-blue-700'
          >
            Done
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
export default VariablesEditorDialog;
