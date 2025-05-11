import { useTranslation } from 'react-i18next';
import i18n from '@/i18n/i18n'; // Adjust the import path as needed

export const LanguageSwitcher = () => {
  const { t } = useTranslation();

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    // Optional: Save preference to localStorage
    localStorage.setItem('userLanguage', lng);
  };

  return (
    <div className="language-switcher">
      <button onClick={() => changeLanguage('en')}>English</button>
      <button onClick={() => changeLanguage('fr')}>Français</button>
    </div>
  );
};