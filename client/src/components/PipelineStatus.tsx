import { Check, Loader2, AlertCircle, Circle } from 'lucide-react';
import { usePipelineStore } from '../store/pipelineStore';
import { useSettingsStore } from '../store/settingsStore';
import type { AgentStatus } from '../types';

const STEP_LABELS_CN = ['架构设计', '套件生成', '质量审核', '优化完善', '功能测试'];
const STEP_LABELS_EN = ['Architecture', 'Generation', 'Review', 'Optimization', 'Testing'];

function StepIcon({ status }: { status: AgentStatus }) {
  const iconStyle = { width: 16, height: 16 };
  
  switch (status) {
    case 'running':
      return <Loader2 style={{ ...iconStyle, animation: 'spin 1s linear infinite' }} />;
    case 'completed':
      return <Check style={iconStyle} />;
    case 'error':
      return <AlertCircle style={iconStyle} />;
    default:
      return <Circle style={{ ...iconStyle, opacity: 0.3 }} />;
  }
}

function getStepColor(status: AgentStatus): string {
  switch (status) {
    case 'running':
      return 'var(--accent-cyan)';
    case 'completed':
      return 'var(--accent-green)';
    case 'error':
      return 'var(--accent-red)';
    default:
      return 'var(--text-muted)';
  }
}

export function PipelineStatus() {
  const { steps, currentStep, review, promptSuite } = usePipelineStore();
  const { language } = useSettingsStore();
  const stepLabels = language === 'en' ? STEP_LABELS_EN : STEP_LABELS_CN;

  return (
    <div style={{
      padding: '20px 24px',
      background: 'var(--bg-card)',
      borderRadius: '16px',
      border: '1px solid var(--border-color)'
    }}>
      {/* 进度条 */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px'
      }}>
        {stepLabels.map((label, index) => {
          const status = index < steps.length ? steps[index].status : 'idle';
          const color = getStepColor(status);
          const isActive = index === currentStep;
          
          return (
            <div key={label} style={{ display: 'flex', alignItems: 'center' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 12px',
                borderRadius: '8px',
                background: isActive ? 'rgba(0, 245, 255, 0.1)' : 'transparent',
                border: isActive ? '1px solid var(--accent-cyan)' : '1px solid transparent',
                transition: 'all 0.3s'
              }}>
                <div style={{ color }}>
                  <StepIcon status={status} />
                </div>
                <span style={{
                  fontSize: '13px',
                  fontWeight: isActive ? 600 : 400,
                  color: isActive ? 'var(--text-primary)' : 'var(--text-secondary)'
                }}>
                  {label}
                </span>
              </div>
              
              {index < stepLabels.length - 1 && (
                <div style={{
                  width: '40px',
                  height: '2px',
                  margin: '0 4px',
                  background: index < currentStep ? 'var(--accent-cyan)' : 'var(--border-color)',
                  transition: 'background 0.3s'
                }} />
              )}
            </div>
          );
        })}
      </div>

      {/* 状态信息 */}
      <div style={{
        display: 'flex',
        gap: '24px',
        paddingTop: '12px',
        borderTop: '1px solid var(--border-color)'
      }}>
        {review && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {language === 'en' ? 'Score:' : '当前评分:'}
            </span>
            <span style={{ 
              fontSize: '14px', 
              fontWeight: 600,
              color: review.score >= 8 ? 'var(--accent-green)' : 
                     review.score >= 6 ? 'var(--accent-yellow)' : 'var(--accent-red)'
            }}>
              {review.score}/10
            </span>
          </div>
        )}

        {promptSuite && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              {language === 'en' ? 'Roles:' : '角色数:'}
            </span>
            <span style={{ 
              fontSize: '14px', 
              fontWeight: 600,
              color: 'var(--accent-purple)'
            }}>
              {promptSuite.total_roles}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
