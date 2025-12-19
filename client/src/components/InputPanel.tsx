import { useState, useEffect } from 'react';
import { Rocket, Sparkles, Pause, Play, X, Upload, RotateCcw, Clock } from 'lucide-react';
import { usePipelineStore } from '../store/pipelineStore';
import { useSettingsStore } from '../store/settingsStore';
import { PROMPT_TYPES, PROMPT_TYPES_EN, PROMPT_TYPE_TEMPLATES_CN, PROMPT_TYPE_TEMPLATES_EN } from '../config/prompts';
import { getIncompleteTasks, recoverPipeline, subscribePipelineEvents, type IncompleteTask } from '../services/api';
import { t } from '../i18n';

export function InputPanel() {
  const [description, setDescription] = useState('');
  const [promptType, setPromptType] = useState('programmer');
  const [incompleteTasks, setIncompleteTasks] = useState<IncompleteTask[]>([]);
  const [showIncompleteTasks, setShowIncompleteTasks] = useState(false);
  const [recovering, setRecovering] = useState(false);
  
  const { 
    isRunning, 
    isPaused, 
    start,
    pause, 
    resume, 
    cancel,
    reset,
    importSuite,
    setTaskId,
    handleEvent
  } = usePipelineStore();
  const { defaultModel, language } = useSettingsStore();
  
  const promptTypes = language === 'en' ? PROMPT_TYPES_EN : PROMPT_TYPES;
  const promptTemplates = language === 'en' ? PROMPT_TYPE_TEMPLATES_EN : PROMPT_TYPE_TEMPLATES_CN;
  const tr = (key: Parameters<typeof t>[0]) => t(key, language);
  
  // 处理类型选择变化，自动填充提示文字
  const handleTypeChange = (newType: string) => {
    setPromptType(newType);
    // 检查当前内容是否是任意语言的模板（中文或英文）
    const allTemplates = [...Object.values(PROMPT_TYPE_TEMPLATES_CN), ...Object.values(PROMPT_TYPE_TEMPLATES_EN)];
    const isCurrentTemplate = allTemplates.some(
      template => description === template || description.startsWith(template.split('\n')[0])
    );
    if (!description.trim() || isCurrentTemplate) {
      setDescription(promptTemplates[newType] || '');
    }
  };

  // 语言切换时，如果当前内容是模板，则更新为新语言的模板
  useEffect(() => {
    const allTemplates = [...Object.values(PROMPT_TYPE_TEMPLATES_CN), ...Object.values(PROMPT_TYPE_TEMPLATES_EN)];
    const isCurrentTemplate = allTemplates.some(
      template => description === template || description.startsWith(template.split('\n')[0])
    );
    if (isCurrentTemplate) {
      setDescription(promptTemplates[promptType] || '');
    }
  }, [language]);

  // 加载未完成任务
  useEffect(() => {
    loadIncompleteTasks();
  }, []);

  const loadIncompleteTasks = async () => {
    try {
      const tasks = await getIncompleteTasks();
      setIncompleteTasks(tasks);
    } catch (error) {
      console.error('Failed to load incomplete tasks:', error);
    }
  };

  const handleStart = () => {
    if (!description.trim()) return;
    reset();
    start(description, promptType, defaultModel);
  };

  const handleRecover = async (task: IncompleteTask) => {
    if (recovering || isRunning) return;
    
    setRecovering(true);
    try {
      reset();
      const result = await recoverPipeline(task.task_id, true);
      
      if (result.resumed) {
        // 设置任务 ID 并订阅事件
        setTaskId(result.taskId);
        
        const eventSource = subscribePipelineEvents(result.taskId);
        eventSource.onmessage = (event) => {
          const data = JSON.parse(event.data);
          handleEvent(data);
          
          if (['pipeline_completed', 'pipeline_error', 'pipeline_cancelled'].includes(data.type)) {
            eventSource.close();
            loadIncompleteTasks(); // 刷新列表
          }
        };
        eventSource.onerror = () => {
          eventSource.close();
        };
        
        setShowIncompleteTasks(false);
      }
    } catch (error) {
      alert(tr('recoverFailed') + ': ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setRecovering(false);
    }
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      
      try {
        const text = await file.text();
        const data = JSON.parse(text);
        
        const suite = data.promptSuite || data;
        
        if (suite.prompts && Array.isArray(suite.prompts)) {
          importSuite(suite);
          alert(`${tr('importSuccess')}: ${suite.system_name || 'Unnamed'}, ${suite.prompts.length} ${tr('roles')}`);
        } else {
          alert(tr('importFailed'));
        }
      } catch (error) {
        alert(tr('importFailed') + ': ' + (error instanceof Error ? error.message : 'Unknown error'));
      }
    };
    input.click();
  };

  const buttonBaseStyle: React.CSSProperties = {
    padding: '10px 16px',
    borderRadius: '8px',
    border: 'none',
    fontSize: '13px',
    fontWeight: 500,
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    transition: 'all 0.2s'
  };

  return (
    <div style={{
      flex: 1,
      padding: '24px',
      background: 'var(--bg-card)',
      borderRadius: '16px',
      border: '1px solid var(--border-color)',
      display: 'flex',
      flexDirection: 'column',
      minHeight: 0
    }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'space-between',
        marginBottom: '20px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Sparkles size={20} style={{ color: 'var(--accent-cyan)' }} />
          <h2 style={{ fontSize: '16px', fontWeight: 600 }}>{tr('inputTitle')}</h2>
        </div>
        
        <div style={{ display: 'flex', gap: '8px' }}>
          {incompleteTasks.length > 0 && (
            <button
              onClick={() => setShowIncompleteTasks(!showIncompleteTasks)}
              disabled={isRunning}
              style={{
                ...buttonBaseStyle,
                background: showIncompleteTasks ? 'var(--accent-yellow)' : 'var(--bg-secondary)',
                color: showIncompleteTasks ? '#000' : 'var(--text-secondary)',
                border: '1px solid var(--border-color)',
                opacity: isRunning ? 0.5 : 1,
                position: 'relative'
              }}
            >
              <RotateCcw size={14} />
              {tr('recoverTask')}
              <span style={{
                position: 'absolute',
                top: '-6px',
                right: '-6px',
                background: 'var(--accent-red)',
                color: '#fff',
                fontSize: '10px',
                padding: '2px 6px',
                borderRadius: '10px',
                fontWeight: 600
              }}>
                {incompleteTasks.length}
              </span>
            </button>
          )}
          <button
            onClick={handleImport}
            disabled={isRunning}
            style={{
              ...buttonBaseStyle,
              background: 'var(--bg-secondary)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-color)',
              opacity: isRunning ? 0.5 : 1
            }}
          >
            <Upload size={14} />
            {tr('importSuite')}
          </button>
        </div>
      </div>

      {/* 未完成任务列表 */}
      {showIncompleteTasks && incompleteTasks.length > 0 && (
        <div style={{
          marginBottom: '16px',
          padding: '12px',
          borderRadius: '8px',
          background: 'var(--bg-secondary)',
          border: '1px solid var(--accent-yellow)',
        }}>
          <div style={{ 
            fontSize: '12px', 
            color: 'var(--accent-yellow)', 
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <Clock size={12} />
            {tr('incompleteTasks')}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {incompleteTasks.map(task => (
              <div
                key={task.task_id}
                onClick={() => handleRecover(task)}
                style={{
                  padding: '10px 12px',
                  borderRadius: '6px',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-color)',
                  cursor: recovering ? 'wait' : 'pointer',
                  transition: 'all 0.2s',
                  opacity: recovering ? 0.6 : 1
                }}
                onMouseEnter={(e) => {
                  if (!recovering) e.currentTarget.style.borderColor = 'var(--accent-cyan)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--border-color)';
                }}
              >
                <div style={{ 
                  fontSize: '13px', 
                  color: 'var(--text-primary)',
                  marginBottom: '4px',
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {task.description.slice(0, 50)}{task.description.length > 50 ? '...' : ''}
                </div>
                <div style={{ 
                  fontSize: '11px', 
                  color: 'var(--text-muted)',
                  display: 'flex',
                  justifyContent: 'space-between'
                }}>
                  <span>{tr('progress')}: {task.completed_roles}/{task.total_roles} {tr('roles')}</span>
                  <span>{new Date(task.updated_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginBottom: '16px' }}>
        <select 
          value={promptType} 
          onChange={(e) => handleTypeChange(e.target.value)}
          disabled={isRunning}
          style={{
            width: '100%',
            padding: '12px 16px',
            borderRadius: '8px',
            border: '1px solid var(--border-color)',
            background: 'var(--bg-secondary)',
            color: 'var(--text-primary)',
            fontSize: '14px',
            cursor: 'pointer',
            outline: 'none'
          }}
        >
          {promptTypes.map(pt => (
            <option key={pt.value} value={pt.value}>{pt.label}</option>
          ))}
        </select>
      </div>

      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder={tr('descriptionPlaceholder')}
        disabled={isRunning}
        style={{
          flex: 1,
          width: '100%',
          minHeight: '300px',
          padding: '16px',
          borderRadius: '12px',
          border: '1px solid var(--border-color)',
          background: 'var(--bg-secondary)',
          color: 'var(--text-primary)',
          fontSize: '14px',
          lineHeight: 1.6,
          resize: 'none',
          outline: 'none',
          fontFamily: 'inherit'
        }}
      />

      {/* 主按钮区域 */}
      {!isRunning ? (
        <button
          onClick={handleStart}
          disabled={!description.trim()}
          style={{
            width: '100%',
            marginTop: '16px',
            padding: '14px 24px',
            borderRadius: '12px',
            border: 'none',
            background: !description.trim() ? 'var(--bg-hover)' : 'var(--gradient-primary)',
            color: !description.trim() ? 'var(--text-muted)' : '#0a0a0f',
            fontSize: '15px',
            fontWeight: 600,
            cursor: !description.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            transition: 'all 0.2s'
          }}
        >
          <Rocket size={18} />
          {tr('startGenerate')}
        </button>
      ) : (
        <div style={{ 
          display: 'flex', 
          gap: '8px', 
          marginTop: '16px' 
        }}>
          <button
            onClick={isPaused ? resume : pause}
            style={{
              ...buttonBaseStyle,
              flex: 1,
              justifyContent: 'center',
              background: isPaused ? 'var(--accent-green)' : 'var(--accent-yellow)',
              color: '#000'
            }}
          >
            {isPaused ? (
              <>
                <Play size={16} />
                {tr('resume')}
              </>
            ) : (
              <>
                <Pause size={16} />
                {tr('pause')}
              </>
            )}
          </button>
          
          <button
            onClick={cancel}
            style={{
              ...buttonBaseStyle,
              flex: 1,
              justifyContent: 'center',
              background: 'var(--accent-red)',
              color: '#fff'
            }}
          >
            <X size={16} />
            {tr('cancel')}
          </button>
        </div>
      )}

      {/* 运行状态指示 */}
      {isRunning && (
        <div style={{
          marginTop: '12px',
          padding: '8px 12px',
          borderRadius: '6px',
          background: isPaused ? 'rgba(245, 158, 11, 0.1)' : 'rgba(6, 182, 212, 0.1)',
          border: `1px solid ${isPaused ? 'var(--accent-yellow)' : 'var(--accent-cyan)'}`,
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isPaused ? 'var(--accent-yellow)' : 'var(--accent-cyan)',
            animation: isPaused ? 'none' : 'pulse-glow 1.5s ease-in-out infinite'
          }} />
          <span style={{ 
            fontSize: '12px', 
            color: isPaused ? 'var(--accent-yellow)' : 'var(--accent-cyan)' 
          }}>
            {isPaused ? tr('paused') : tr('running')}
          </span>
        </div>
      )}
    </div>
  );
}
