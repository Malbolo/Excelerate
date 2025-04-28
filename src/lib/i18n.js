import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import enTranslations from '../locales/en.json';
import koTranslations from '../locales/ko.json';

i18n.use(initReactI18next).init({
  resources: {
    en: { translation: enTranslations },
    ko: { translation: koTranslations },
  },
  lng: 'ko',
  fallbackLng: 'en',
  interpolation: {
    escapeValue: false,
  },
});

export default i18n;
