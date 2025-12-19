// API client for Flask backend
import type { Settings, HistoryRecord, SuiteListItem, PromptSuite } from '../types';

const API_BASE = '/api';

// ==================== Pipeline API ====================

export interface StartPipelineParams {
  description: string;
  type: string;
  model: string;
}

export async function startPipeline(params: StartPipelineParams): Promise<{ taskId: string }> {
  const response = await fetch(`${API_BASE}/pipeline/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}

export function subscribePipelineEvents(taskId: string): EventSource {
  return new EventSource(`${API_BASE}/pipeline/stream?taskId=${taskId}`);
}

export async function pausePipeline(taskId: string): Promise<void> {
  await fetch(`${API_BASE}/pipeline/pause`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ taskId })
  });
}

export async function resumePipeline(taskId: string): Promise<void> {
  await fetch(`${API_BASE}/pipeline/resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ taskId })
  });
}

export async function cancelPipeline(taskId: string): Promise<void> {
  await fetch(`${API_BASE}/pipeline/cancel`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ taskId })
  });
}

// ==================== 断点恢复 API ====================

export interface IncompleteTask {
  task_id: string;
  description: string;
  status: string;
  completed_roles: number;
  total_roles: number;
  updated_at: string;
}

export async function getIncompleteTasks(): Promise<IncompleteTask[]> {
  const response = await fetch(`${API_BASE}/pipeline/incomplete`);
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}

export async function recoverPipeline(taskId: string, parallel: boolean = true): Promise<{ taskId: string; resumed: boolean }> {
  const response = await fetch(`${API_BASE}/pipeline/recover`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ taskId, parallel })
  });
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}


// ==================== Settings API ====================

export async function getSettings(): Promise<Settings> {
  const response = await fetch(`${API_BASE}/settings`);
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}

export async function saveSettings(settings: Settings): Promise<void> {
  const response = await fetch(`${API_BASE}/settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings)
  });
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
}

// ==================== Suites API ====================

export async function getSuites(): Promise<SuiteListItem[]> {
  const response = await fetch(`${API_BASE}/suites`);
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}

export async function getSuiteDetail(name: string): Promise<any> {
  const response = await fetch(`${API_BASE}/suites/${encodeURIComponent(name)}`);
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}

export interface SaveSuiteParams {
  requirement: any;
  promptSuite: PromptSuite | null;
  review: any;
  testResult: any;
  versions: any[];
  finalPrompt: string;
}

export async function saveSuite(params: SaveSuiteParams): Promise<{ folder: string; path: string; files: string[] }> {
  const response = await fetch(`${API_BASE}/save-suite`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params)
  });
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}

// ==================== History API ====================

export async function getHistory(): Promise<HistoryRecord[]> {
  const response = await fetch(`${API_BASE}/history`);
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}

export async function addHistory(record: Omit<HistoryRecord, 'id' | 'createdAt'>): Promise<HistoryRecord> {
  const response = await fetch(`${API_BASE}/history`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(record)
  });
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
  return result.data;
}

export async function deleteHistory(id: string): Promise<void> {
  const response = await fetch(`${API_BASE}/history/${id}`, { method: 'DELETE' });
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
}

export async function clearHistory(): Promise<void> {
  const response = await fetch(`${API_BASE}/history`, { method: 'DELETE' });
  const result = await response.json();
  if (!result.success) throw new Error(result.error);
}
