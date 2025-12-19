import { Factory, Settings, Globe } from 'lucide-react';
import { useSettingsStore } from '../store/settingsStore';
import { t } from '../i18n';
import type { Language } from '../types';

interface Props {
  onSettingsClick: () => void;
}

export function Header({ onSettingsClick }: Props) {
  const { language, setLanguage, save } = useSettingsStore();
  
  const toggleLanguage = async () => {
    const newLang: Language = language === 'cn' ? 'en' : 'cn';
    setLanguage(newLang);
    await save({ language: newLang });
  };

  return (
    <header style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px 32px',
      borderBottom: '1px solid var(--border-color)',
      background: 'var(--bg-secondary)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <div style={{
          width: '40px',
          height: '40px',
          borderRadius: '10px',
          background: 'var(--gradient-primary)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <Factory size={24} color="#0a0a0f" />
        </div>
        <div>
          <h1 style={{ 
            fontSize: '20px', 
            fontWeight: 700,
            background: 'var(--gradient-primary)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}>
            {t('appTitle', language)}
          </h1>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            {t('appSubtitle', language)}
          </p>
        </div>
      </div>
      
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        {/* Language Toggle */}
        <button 
          onClick={toggleLanguage}
          style={{
            height: '40px',
            padding: '0 12px',
            borderRadius: '10px',
            border: '1px solid var(--border-color)',
            background: 'var(--bg-card)',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '13px',
            fontWeight: 500,
            transition: 'all 0.2s'
          }}
        >
          <Globe size={16} />
          {language === 'cn' ? '中文' : 'EN'}
        </button>
        
        {/* Settings Button */}
        <button 
          onClick={onSettingsClick}
          style={{
            width: '40px',
            height: '40px',
            borderRadius: '10px',
            border: '1px solid var(--border-color)',
            background: 'var(--bg-card)',
            color: 'var(--text-secondary)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 0.2s'
          }}
        >
          <Settings size={20} />
        </button>
      </div>
    </header>
  );
}
