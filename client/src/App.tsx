import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { InputPanel } from './components/InputPanel';
import { AgentPanel } from './components/AgentPanel';
import { ResultPanel } from './components/ResultPanel';
import { SettingsModal } from './components/SettingsModal';
import { useSettingsStore } from './store/settingsStore';

function App() {
  const [showSettings, setShowSettings] = useState(false);
  const { load } = useSettingsStore();

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'var(--bg-primary)',
      overflow: 'hidden'
    }}>
      <Header onSettingsClick={() => setShowSettings(true)} />
      
      <main style={{
        flex: 1,
        padding: '20px 24px',
        display: 'grid',
        gridTemplateColumns: '420px 1fr',
        gap: '20px',
        minHeight: 0,
        maxWidth: '1800px',
        margin: '0 auto',
        width: '100%'
      }}>
        {/* 左侧：Agent 执行过程 */}
        <div style={{
          minHeight: 0,
          overflow: 'auto'
        }}>
          <AgentPanel />
        </div>
        
        {/* 右侧：输入 + 结果 */}
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '16px',
          minHeight: 0,
          overflow: 'hidden'
        }}>
          {/* 输入面板 - 占据大部分空间 */}
          <div style={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
            <InputPanel />
          </div>
          
          {/* 结果状态（简化版） - 固定高度 */}
          <ResultPanel />
        </div>
      </main>

      <SettingsModal 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
    </div>
  );
}

export default App;
