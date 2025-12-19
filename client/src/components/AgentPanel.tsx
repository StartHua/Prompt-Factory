import { Bot, Brain, Shield, Wand2, FlaskConical, Users, CheckCircle, Circle, Loader } from 'lucide-react';
import { usePipelineStore } from '../store/pipelineStore';
import { useSettingsStore } from '../store/settingsStore';
import type { AgentType } from '../types';

const AGENT_CONFIG_CN: Record<AgentType, { icon: typeof Bot; label: string; color: string }> = {
  analyzer: { icon: Brain, label: '系统架构设计', color: 'var(--accent-cyan)' },
  generator: { icon: Wand2, label: '角色生成', color: 'var(--accent-purple)' },
  reviewer: { icon: Shield, label: '质量审核', color: 'var(--accent-yellow)' },
  optimizer: { icon: Bot, label: '优化完善', color: 'var(--accent-green)' },
  tester: { icon: FlaskConical, label: '整体测试', color: 'var(--accent-pink)' }
};

const AGENT_CONFIG_EN: Record<AgentType, { icon: typeof Bot; label: string; color: string }> = {
  analyzer: { icon: Brain, label: 'Architecture Design', color: 'var(--accent-cyan)' },
  generator: { icon: Wand2, label: 'Role Generation', color: 'var(--accent-purple)' },
  reviewer: { icon: Shield, label: 'Quality Review', color: 'var(--accent-yellow)' },
  optimizer: { icon: Bot, label: 'Optimization', color: 'var(--accent-green)' },
  tester: { icon: FlaskConical, label: 'Testing', color: 'var(--accent-pink)' }
};

const ROLE_STATUS_CONFIG_CN = {
  pending: { icon: Circle, color: 'var(--text-muted)', label: '等待中' },
  generating: { icon: Loader, color: 'var(--accent-purple)', label: '生成中' },
  reviewing: { icon: Shield, color: 'var(--accent-yellow)', label: '审核中' },
  optimizing: { icon: Bot, color: 'var(--accent-green)', label: '优化中' },
  completed: { icon: CheckCircle, color: 'var(--accent-green)', label: '完成' },
  error: { icon: Circle, color: 'var(--accent-red)', label: '错误' }
};

const ROLE_STATUS_CONFIG_EN = {
  pending: { icon: Circle, color: 'var(--text-muted)', label: 'Pending' },
  generating: { icon: Loader, color: 'var(--accent-purple)', label: 'Generating' },
  reviewing: { icon: Shield, color: 'var(--accent-yellow)', label: 'Reviewing' },
  optimizing: { icon: Bot, color: 'var(--accent-green)', label: 'Optimizing' },
  completed: { icon: CheckCircle, color: 'var(--accent-green)', label: 'Done' },
  error: { icon: Circle, color: 'var(--accent-red)', label: 'Error' }
};

export function AgentPanel() {
  const { steps, review, testResult, systemArchitecture, roleStates, currentRoleIndex, totalRoles } = usePipelineStore();
  const { language } = useSettingsStore();
  const AGENT_CONFIG = language === 'en' ? AGENT_CONFIG_EN : AGENT_CONFIG_CN;
  const ROLE_STATUS_CONFIG = language === 'en' ? ROLE_STATUS_CONFIG_EN : ROLE_STATUS_CONFIG_CN;

  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      gap: '12px',
      padding: '16px',
      background: 'var(--bg-card)',
      borderRadius: '16px',
      border: '1px solid var(--border-color)',
      overflow: 'hidden'
    }}>
      <h3 style={{ 
        fontSize: '14px', 
        fontWeight: 600, 
        color: 'var(--text-secondary)',
        flexShrink: 0
      }}>
        {language === 'en' ? 'Agent Execution' : 'Agent 执行过程'}
      </h3>
      
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: '12px',
        overflowY: 'auto',
        paddingRight: '8px'
      }}>
        {steps.map((step) => {
          const config = AGENT_CONFIG[step.type];
          const Icon = config.icon;
          const isActive = step.status === 'running';
          const hasOutput = step.output.length > 0;
          
          return (
            <div
              key={step.type}
              style={{
                padding: '16px',
                borderRadius: '12px',
                border: `1px solid ${isActive ? config.color : 'var(--border-color)'}`,
                background: isActive ? `${config.color}10` : 'var(--bg-card)',
                transition: 'all 0.3s'
              }}
            >
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                marginBottom: hasOutput ? '12px' : 0
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  background: `${config.color}20`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: config.color
                }}>
                  <Icon size={18} />
                </div>
                <div>
                  <div style={{ fontSize: '14px', fontWeight: 600 }}>
                    {config.label}
                  </div>
                  {step.thinking.length > 0 && (
                    <div style={{ 
                      fontSize: '12px', 
                      color: 'var(--text-muted)',
                      marginTop: '2px'
                    }}>
                      {step.thinking[step.thinking.length - 1]}
                    </div>
                  )}
                </div>
                {isActive && (
                  <div style={{
                    marginLeft: 'auto',
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: config.color,
                    animation: 'pulse-glow 1.5s ease-in-out infinite'
                  }} />
                )}
              </div>
              
              {hasOutput && (
                <div style={{
                  maxHeight: '120px',
                  overflowY: 'auto',
                  padding: '12px',
                  borderRadius: '8px',
                  background: 'var(--bg-secondary)',
                  fontSize: '11px',
                  fontFamily: 'monospace',
                  color: 'var(--text-secondary)',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word'
                }}>
                  {step.output.slice(0, 400)}
                  {step.output.length > 400 && '...'}
                </div>
              )}
            </div>
          );
        })}
        
        {/* 系统架构卡片 */}
        {systemArchitecture && (
          <div style={{
            padding: '16px',
            borderRadius: '12px',
            border: '1px solid var(--accent-cyan)',
            background: 'rgba(6, 182, 212, 0.1)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              marginBottom: '12px'
            }}>
              <Users size={16} style={{ color: 'var(--accent-cyan)' }} />
              <span style={{ fontSize: '14px', fontWeight: 600 }}>
                {systemArchitecture.system_name}
              </span>
            </div>
            
            <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
              {systemArchitecture.system_description?.slice(0, 100)}
              {(systemArchitecture.system_description?.length || 0) > 100 && '...'}
            </div>
            
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {systemArchitecture.roles?.map((role, i) => (
                <span key={i} style={{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  background: role.type === 'core' ? 'rgba(59, 130, 246, 0.2)' :
                             role.type === 'quality' ? 'rgba(16, 185, 129, 0.2)' :
                             'rgba(139, 92, 246, 0.2)',
                  color: role.type === 'core' ? '#3b82f6' :
                         role.type === 'quality' ? 'var(--accent-green)' :
                         'var(--accent-purple)'
                }}>
                  {role.name}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* 逐角色处理进度 */}
        {roleStates.length > 0 && (
          <div style={{
            padding: '16px',
            borderRadius: '12px',
            border: '1px solid var(--accent-purple)',
            background: 'rgba(139, 92, 246, 0.1)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '12px'
            }}>
              <span style={{ fontSize: '14px', fontWeight: 600 }}>
                {language === 'en' ? 'Role Progress' : '角色处理进度'}
              </span>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                {roleStates.filter(r => r.status === 'completed').length}/{totalRoles}
              </span>
            </div>
            
            {/* 进度条 */}
            <div style={{
              height: '4px',
              background: 'var(--bg-secondary)',
              borderRadius: '2px',
              marginBottom: '12px',
              overflow: 'hidden'
            }}>
              <div style={{
                height: '100%',
                width: `${(roleStates.filter(r => r.status === 'completed').length / totalRoles) * 100}%`,
                background: 'linear-gradient(90deg, var(--accent-purple), var(--accent-cyan))',
                borderRadius: '2px',
                transition: 'width 0.3s'
              }} />
            </div>
            
            {/* 角色列表 */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {roleStates.map((role, i) => {
                const statusConfig = ROLE_STATUS_CONFIG[role.status];
                const StatusIcon = statusConfig.icon;
                const isActive = i === currentRoleIndex && role.status !== 'completed';
                
                return (
                  <div key={role.roleId} style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px',
                    borderRadius: '6px',
                    background: isActive ? 'rgba(139, 92, 246, 0.2)' : 'transparent',
                    border: isActive ? '1px solid var(--accent-purple)' : '1px solid transparent'
                  }}>
                    <StatusIcon 
                      size={14} 
                      style={{ 
                        color: statusConfig.color,
                        animation: role.status === 'generating' || role.status === 'reviewing' || role.status === 'optimizing' 
                          ? 'spin 1s linear infinite' 
                          : 'none'
                      }} 
                    />
                    <span style={{ 
                      fontSize: '12px', 
                      flex: 1,
                      color: role.status === 'completed' ? 'var(--text-primary)' : 'var(--text-secondary)'
                    }}>
                      {i + 1}. {role.roleName}
                    </span>
                    <span style={{ 
                      fontSize: '11px', 
                      color: statusConfig.color,
                      padding: '2px 6px',
                      borderRadius: '4px',
                      background: `${statusConfig.color}20`
                    }}>
                      {role.status === 'completed' && role.finalScore > 0 
                        ? (language === 'en' ? `${role.finalScore}pts` : `${role.finalScore}分`)
                        : statusConfig.label}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* 审核评分卡片 */}
        {review && (
          <div style={{
            padding: '16px',
            borderRadius: '12px',
            border: '1px solid var(--accent-yellow)',
            background: 'rgba(245, 158, 11, 0.1)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '12px'
            }}>
              <span style={{ fontSize: '14px', fontWeight: 600 }}>
                {language === 'en' ? 'Review Score' : '审核评分'}
              </span>
              <span style={{
                fontSize: '24px',
                fontWeight: 700,
                color: review.score >= 8 ? 'var(--accent-green)' : 
                       review.score >= 6 ? 'var(--accent-yellow)' : 'var(--accent-red)'
              }}>
                {review.score}/10
              </span>
            </div>
            
            {review.strengths && review.strengths.length > 0 && (
              <div style={{ marginBottom: '8px' }}>
                <div style={{ fontSize: '12px', color: 'var(--accent-green)', marginBottom: '4px' }}>
                  {language === 'en' ? '✓ Strengths' : '✓ 优点'}
                </div>
                {review.strengths.slice(0, 2).map((s, i) => (
                  <div key={i} style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    • {typeof s === 'string' ? s : s}
                  </div>
                ))}
              </div>
            )}
            
            {review.weaknesses && review.weaknesses.length > 0 && (
              <div>
                <div style={{ fontSize: '12px', color: 'var(--accent-red)', marginBottom: '4px' }}>
                  {language === 'en' ? '✗ Improvements' : '✗ 待改进'}
                </div>
                {review.weaknesses.slice(0, 2).map((w, i) => (
                  <div key={i} style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                    • {typeof w === 'string' ? w : w.issue}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* 测试结果卡片 */}
        {testResult && (
          <div style={{
            padding: '16px',
            borderRadius: '12px',
            border: '1px solid var(--accent-pink)',
            background: 'rgba(236, 72, 153, 0.1)'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '12px'
            }}>
              <span style={{ fontSize: '14px', fontWeight: 600 }}>
                {language === 'en' ? 'Test Results' : '测试结果'}
              </span>
              <span style={{
                fontSize: '14px',
                fontWeight: 600,
                padding: '4px 12px',
                borderRadius: '6px',
                background: testResult.summary.verdict === '通过' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                color: testResult.summary.verdict === '通过' ? 'var(--accent-green)' : 'var(--accent-red)'
              }}>
                {testResult.summary.verdict}
              </span>
            </div>
            
            <div style={{ display: 'flex', gap: '16px', fontSize: '12px' }}>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>{language === 'en' ? 'Pass Rate: ' : '通过率: '}</span>
                <span style={{ color: 'var(--accent-green)', fontWeight: 600 }}>
                  {(testResult.summary.pass_rate * 100).toFixed(0)}%
                </span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>{language === 'en' ? 'Passed: ' : '通过: '}</span>
                <span style={{ color: 'var(--accent-green)' }}>{testResult.summary.passed}</span>
              </div>
              <div>
                <span style={{ color: 'var(--text-muted)' }}>{language === 'en' ? 'Failed: ' : '失败: '}</span>
                <span style={{ color: 'var(--accent-red)' }}>{testResult.summary.failed}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
