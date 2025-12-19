import { FolderOpen, CheckCircle, Loader2 } from 'lucide-react';
import { usePipelineStore } from '../store/pipelineStore';
import { useSettingsStore } from '../store/settingsStore';

export function ResultPanel() {
  const { currentStep, promptSuite, isRunning } = usePipelineStore();
  const { language } = useSettingsStore();

  const isCompleted = currentStep >= 4 && promptSuite;

  return (
    <div style={{
      padding: '16px',
      background: 'var(--bg-card)',
      borderRadius: '12px',
      border: '1px solid var(--border-color)'
    }}>
      <h3 style={{ 
        fontSize: '14px', 
        fontWeight: 600, 
        color: 'var(--text-secondary)',
        marginBottom: '12px'
      }}>
        {language === 'en' ? 'Output' : '输出结果'}
      </h3>

      {isRunning ? (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '12px',
          background: 'rgba(6, 182, 212, 0.1)',
          borderRadius: '8px',
          border: '1px solid var(--accent-cyan)'
        }}>
          <Loader2 size={18} style={{ color: 'var(--accent-cyan)', animation: 'spin 1s linear infinite' }} />
          <span style={{ fontSize: '13px', color: 'var(--accent-cyan)' }}>
            {language === 'en' ? 'Generating prompts...' : '正在生成提示词...'}
          </span>
        </div>
      ) : isCompleted ? (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '12px',
          background: 'rgba(16, 185, 129, 0.1)',
          borderRadius: '8px',
          border: '1px solid var(--accent-green)'
        }}>
          <CheckCircle size={18} style={{ color: 'var(--accent-green)' }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontSize: '13px', color: 'var(--accent-green)', fontWeight: 500 }}>
              {language === 'en' ? 'Generation complete!' : '生成完成！'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              {promptSuite?.total_roles} {language === 'en' ? 'roles generated' : '个角色已生成'}
            </div>
          </div>
          <FolderOpen size={16} style={{ color: 'var(--text-muted)' }} />
        </div>
      ) : (
        <div style={{
          padding: '12px',
          background: 'var(--bg-secondary)',
          borderRadius: '8px',
          border: '1px solid var(--border-color)',
          color: 'var(--text-muted)',
          fontSize: '13px',
          textAlign: 'center'
        }}>
          {language === 'en' ? 'Results will be saved to result/ folder' : '结果将保存到 result/ 目录'}
        </div>
      )}
    </div>
  );
}
