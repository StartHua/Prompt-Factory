// Internationalization (i18n) configuration
import type { Language } from '../types';

export const translations = {
  cn: {
    // Header
    appTitle: 'Prompt Factory',
    appSubtitle: '提示词工厂',
    
    // Input Panel
    inputTitle: '需求输入',
    importSuite: '导入套件',
    recoverTask: '恢复任务',
    incompleteTasks: '未完成的任务（点击恢复）',
    progress: '进度',
    roles: '角色',
    selectType: '选择类型',
    descriptionPlaceholder: '描述你需要的提示词，例如：我需要一个全栈程序员助手，精通 Java 和 React，能帮我修改代码、解决 bug、优化性能...',
    startGenerate: '开始生成',
    pause: '暂停',
    resume: '继续',
    cancel: '取消',
    running: '正在生成中...',
    paused: '已暂停，点击继续',
    
    // Settings
    settings: '设置',
    apiKey: 'API Key',
    apiKeyPlaceholder: '输入你的 API Key',
    baseUrl: 'Base URL',
    defaultModel: '默认模型',
    useStream: '流式输出',
    language: '语言',
    save: '保存',
    saving: '保存中...',
    
    // Pipeline
    analyzer: '需求分析',
    generator: '提示词生成',
    reviewer: '质量审核',
    optimizer: '优化改进',
    tester: '测试验证',
    
    // Status
    idle: '等待中',
    generating: '生成中',
    reviewing: '审核中',
    optimizing: '优化中',
    completed: '已完成',
    error: '错误',
    pending: '待处理',
    
    // Results
    results: '生成结果',
    overview: '概览',
    rolePrompts: '角色提示词',
    score: '评分',
    passThreshold: '通过阈值',
    iterations: '迭代次数',
    
    // Actions
    copy: '复制',
    copied: '已复制',
    download: '下载',
    export: '导出',
    
    // Messages
    noApiKey: '请先配置 API Key',
    invalidRequest: '请求数据无效',
    emptyDescription: '请输入需求描述',
    importSuccess: '导入成功',
    importFailed: '导入失败',
    recoverFailed: '恢复任务失败',
    saveFailed: '保存失败',
    saveSuccess: '保存成功',
  },
  
  en: {
    // Header
    appTitle: 'Prompt Factory',
    appSubtitle: 'AI Prompt Engineering',
    
    // Input Panel
    inputTitle: 'Requirements Input',
    importSuite: 'Import Suite',
    recoverTask: 'Recover Task',
    incompleteTasks: 'Incomplete Tasks (Click to Recover)',
    progress: 'Progress',
    roles: 'roles',
    selectType: 'Select Type',
    descriptionPlaceholder: 'Describe the prompt you need, e.g.: I need a full-stack programmer assistant proficient in Java and React, who can help me modify code, fix bugs, optimize performance...',
    startGenerate: 'Start Generate',
    pause: 'Pause',
    resume: 'Resume',
    cancel: 'Cancel',
    running: 'Generating...',
    paused: 'Paused, click to continue',
    
    // Settings
    settings: 'Settings',
    apiKey: 'API Key',
    apiKeyPlaceholder: 'Enter your API Key',
    baseUrl: 'Base URL',
    defaultModel: 'Default Model',
    useStream: 'Stream Output',
    language: 'Language',
    save: 'Save',
    saving: 'Saving...',
    
    // Pipeline
    analyzer: 'Requirements Analysis',
    generator: 'Prompt Generation',
    reviewer: 'Quality Review',
    optimizer: 'Optimization',
    tester: 'Testing',
    
    // Status
    idle: 'Idle',
    generating: 'Generating',
    reviewing: 'Reviewing',
    optimizing: 'Optimizing',
    completed: 'Completed',
    error: 'Error',
    pending: 'Pending',
    
    // Results
    results: 'Results',
    overview: 'Overview',
    rolePrompts: 'Role Prompts',
    score: 'Score',
    passThreshold: 'Pass Threshold',
    iterations: 'Iterations',
    
    // Actions
    copy: 'Copy',
    copied: 'Copied',
    download: 'Download',
    export: 'Export',
    
    // Messages
    noApiKey: 'Please configure API Key first',
    invalidRequest: 'Invalid request data',
    emptyDescription: 'Please enter requirements description',
    importSuccess: 'Import successful',
    importFailed: 'Import failed',
    recoverFailed: 'Failed to recover task',
    saveFailed: 'Save failed',
    saveSuccess: 'Save successful',
  }
} as const;

export type TranslationKey = keyof typeof translations.cn;

export function t(key: TranslationKey, language: Language = 'cn'): string {
  return translations[language][key] || translations.cn[key] || key;
}

export function createT(language: Language) {
  return (key: TranslationKey) => t(key, language);
}
