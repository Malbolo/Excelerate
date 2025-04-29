import { Check, ChevronsUpDown } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { cn } from '@/lib/utils';

const languages = [
  { code: 'ko', label: '한국어' },
  { code: 'en', label: 'English' },
];

function LanguageSelector() {
  const { i18n } = useTranslation();
  const currentLanguageCode = i18n.language;

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  const currentLanguageLabel =
    languages.find(lang => currentLanguageCode.startsWith(lang.code))?.label ||
    'Language';

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant='outline'
          size='sm'
          className='w-[120px] justify-between'
          aria-label={`Change language, current language: ${currentLanguageLabel}`}
        >
          {currentLanguageLabel}
          <ChevronsUpDown className='ml-2 h-4 w-4 shrink-0 opacity-50' />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align='end' className='w-[120px]'>
        {languages.map(lang => {
          const isActive = currentLanguageCode.startsWith(lang.code);
          return (
            <DropdownMenuItem
              key={lang.code}
              onSelect={() => changeLanguage(lang.code)}
              disabled={isActive}
              aria-current={isActive ? 'true' : 'false'}
            >
              <Check
                className={cn(
                  'mr-2 h-4 w-4',
                  isActive ? 'opacity-100' : 'opacity-0',
                )}
              />
              {lang.label}
            </DropdownMenuItem>
          );
        })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

export default LanguageSelector;
