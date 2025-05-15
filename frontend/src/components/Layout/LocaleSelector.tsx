import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useLocalDate } from '@/store/useLocalDate';

const LOCALES = [
  {
    label: 'Korean',
    value: 'ko-KR',
    place: 'Asia/Seoul',
  },
  {
    label: 'English (US)',
    value: 'en-US',
    place: 'America/New_York',
  },
  {
    label: 'Vietnamese',
    value: 'vi-VN',
    place: 'Asia/Ho_Chi_Minh',
  },
  {
    label: 'Japanese',
    value: 'ja-JP',
    place: 'Asia/Tokyo',
  },
];

const LocaleSelector = () => {
  const { locale, setLocale, setPlace } = useLocalDate();

  const handleLocaleChange = (selectedValue: string) => {
    const selectedFullLocale = LOCALES.find(l => l.value === selectedValue);

    if (selectedFullLocale) {
      setLocale(selectedFullLocale.value);
      setPlace(selectedFullLocale.place);
    }
  };

  const currentLocaleLabel =
    LOCALES.find(l => l.value === locale)?.label || 'Select language';

  return (
    <Select value={locale} onValueChange={handleLocaleChange}>
      <SelectTrigger className='ring-offset-background focus:ring-ring hover:bg-accent hover:text-accent-foreground border-input bg-background w-full justify-start border px-3 py-2 text-sm font-medium focus:ring-2 focus:ring-offset-2 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50'>
        <SelectValue placeholder='Select language'>
          {currentLocaleLabel}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {LOCALES.map(l => (
          <SelectItem key={l.value} value={l.value}>
            {l.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
};

export default LocaleSelector;
