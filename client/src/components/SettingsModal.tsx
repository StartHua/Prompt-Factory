import { useState, useEffect } from 'react';
import { X, Key, Globe, Bot, Eye, EyeOff, Save, Loader2, Zap } from 'lucide-react';
import { useSettingsStore } from '../store/settingsStore';
import { t } from '../i18n';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export function SettingsModal({ isOpen, onClose }: Props) {
  const { apiKey, baseUrl, defaultModel, useStream, language, save, load, isLoading } = useSettingsStore();
  const tr = (key: Parameters<typeof t>[0]) => t(key, language);
  
  const [localApiKey, setLocalApiKey] = useState(apiKey);
  const [localBaseUrl, setLocalBaseUrl] = useState(baseUrl);
  const [localModel, setLocalModel] = useState(defaultModel);
  const [localUseStream, setLocalUseStream] = useState(useStream);
  const [showKey, setShowKey] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');

  useEffect(() => {
    if (isOpen) {
      load();
    }
  }, [isOpen, load]);

  useEffect(() => {
    setLocalApiKey(apiKey);
    setLocalBaseUrl(baseUrl);
    setLocalModel(defaultModel);
    setLocalUseStream(useStream);
  }, [apiKey, baseUrl, defaultModel, useStream]);

  if (!isOpen) return null;

  const handleSave = async () => {
    setSaving(true);
    setSaveStatus('idle');
    
    const success = await save({
      apiKey: localApiKey,
      baseUrl: localBaseUrl,
      defaultModel: localModel,
      useStream: localUseStream
    });
    
    setSaving(false);
    setSaveStatus(success ? 'success' : 'error');
    
    if (success) {
      setTimeout(() => {
        setSaveStatus('idle');
        onClose();
      }, 1000);
    }
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px 16px',
    borderRadius: '8px',
    border: '1px solid var(--border-color)',
    background: 'var(--bg-secondary)',
    color: 'var(--text-primary)',
    fontSize: '14px',
    outline: 'none',
  };

  const labelStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
    fontWeight: 500,
    color: 'var(--text-secondary)',
    marginBottom: '8px',
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        width: '480px',
        background: 'var(--bg-card)',
        borderRadius: '16px',
        border: '1px solid var(--border-color)',
        overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-color)',
        }}>
          <h2 style={{ fontSize: '18px', fontWeight: 600 }}>{tr('settings')}</h2>
          <button
            onClick={onClose}
            style={{
              width: '32px',
              height: '32px',
              borderRadius: '8px',
              border: 'none',
              background: 'var(--bg-hover)',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {isLoading ? (
            <div style={{ 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              padding: '40px',
              color: 'var(--text-muted)'
            }}>
              <Loader2 size={24} style={{ animation: 'spin 1s linear infinite' }} />
              <span style={{ marginLeft: '12px' }}>{language === 'en' ? 'Loading...' : '加载配置中...'}</span>
            </div>
          ) : (
            <>
              {/* API Key */}
              <div>
                <label style={labelStyle}>
                  <Key size={14} />
                  API Key
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showKey ? 'text' : 'password'}
                    value={localApiKey}
                    onChange={(e) => setLocalApiKey(e.target.value)}
                    placeholder={tr('apiKeyPlaceholder')}
                    style={{ ...inputStyle, paddingRight: '44px' }}
                  />
                  <button
                    onClick={() => setShowKey(!showKey)}
                    style={{
                      position: 'absolute',
                      right: '12px',
                      top: '50%',
                      transform: 'translateY(-50%)',
                      background: 'none',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      padding: '4px',
                    }}
                  >
                    {showKey ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>

              {/* Base URL */}
              <div>
                <label style={labelStyle}>
                  <Globe size={14} />
                  API Base URL
                </label>
                <input
                  type="text"
                  value={localBaseUrl}
                  onChange={(e) => setLocalBaseUrl(e.target.value)}
                  placeholder="https://api.openai.com"
                  style={inputStyle}
                />
              </div>

              {/* Default Model */}
              <div>
                <label style={labelStyle}>
                  <Bot size={14} />
                  {tr('defaultModel')}
                </label>
                <input
                  type="text"
                  value={localModel}
                  onChange={(e) => setLocalModel(e.target.value)}
                  placeholder="输入模型名称，如 claude-sonnet-4-5-20251022"
                  style={inputStyle}
                />
              </div>

              {/* Stream Mode */}
              <div>
                <label style={labelStyle}>
                  <Zap size={14} />
                  {language === 'en' ? 'Output Mode' : '输出模式'}
                </label>
                <div style={{ display: 'flex', gap: '12px' }}>
                  <button
                    onClick={() => setLocalUseStream(true)}
                    style={{
                      flex: 1,
                      padding: '12px 16px',
                      borderRadius: '8px',
                      border: `1px solid ${localUseStream ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
                      background: localUseStream ? 'rgba(0, 245, 255, 0.1)' : 'var(--bg-secondary)',
                      color: localUseStream ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                      fontSize: '14px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    {language === 'en' ? 'Stream' : '流式输出'}
                  </button>
                  <button
                    onClick={() => setLocalUseStream(false)}
                    style={{
                      flex: 1,
                      padding: '12px 16px',
                      borderRadius: '8px',
                      border: `1px solid ${!localUseStream ? 'var(--accent-cyan)' : 'var(--border-color)'}`,
                      background: !localUseStream ? 'rgba(0, 245, 255, 0.1)' : 'var(--bg-secondary)',
                      color: !localUseStream ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                      fontSize: '14px',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    {language === 'en' ? 'Complete' : '完整输出'}
                  </button>
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '8px' }}>
                  {localUseStream 
                    ? (language === 'en' ? 'Real-time display, smoother experience' : '实时显示生成内容，体验更流畅')
                    : (language === 'en' ? 'Wait for complete response, better compatibility' : '等待完整响应后显示，兼容性更好')}
                </p>
              </div>

              {/* Info */}
              <div style={{
                padding: '12px 16px',
                borderRadius: '8px',
                background: 'rgba(0, 245, 255, 0.1)',
                border: '1px solid rgba(0, 245, 255, 0.2)',
                fontSize: '12px',
                color: 'var(--text-secondary)',
                lineHeight: 1.6,
              }}>
                {language === 'en' 
                  ? '🔐 Settings will be encrypted and saved to config/settings.enc'
                  : '🔐 配置将加密保存到服务器 config/settings.enc 文件中'}
              </div>

              {saveStatus === 'error' && (
                <div style={{
                  padding: '12px 16px',
                  borderRadius: '8px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid var(--accent-red)',
                  fontSize: '12px',
                  color: 'var(--accent-red)',
                }}>
                  {tr('saveFailed')}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 24px',
          borderTop: '1px solid var(--border-color)',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '12px',
        }}>
          <button
            onClick={onClose}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: '1px solid var(--border-color)',
              background: 'transparent',
              color: 'var(--text-secondary)',
              fontSize: '14px',
              cursor: 'pointer',
            }}
          >
            {tr('cancel')}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || isLoading}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              background: saveStatus === 'success' ? 'var(--accent-green)' : 
                         saveStatus === 'error' ? 'var(--accent-red)' : 
                         'var(--gradient-primary)',
              color: '#0a0a0f',
              fontSize: '14px',
              fontWeight: 600,
              cursor: saving ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              opacity: saving ? 0.7 : 1,
            }}
          >
            {saving ? (
              <Loader2 size={14} style={{ animation: 'spin 1s linear infinite' }} />
            ) : (
              <Save size={14} />
            )}
            {saveStatus === 'success' ? tr('saveSuccess') : 
             saveStatus === 'error' ? tr('saveFailed') : 
             saving ? tr('saving') : tr('save')}
          </button>
        </div>
      </div>
    </div>
  );
}
