import { create } from 'zustand';
import type { AgentState, PipelineState, PromptSuite, RoleProcessState } from '../types';
import { startPipeline, subscribePipelineEvents, pausePipeline, resumePipeline, cancelPipeline } from '../services/api';

const initialAgentStates: AgentState[] = [
  { type: 'analyzer', status: 'idle', output: '', thinking: [] },
  { type: 'generator', status: 'idle', output: '', thinking: [] },
  { type: 'reviewer', status: 'idle', output: '', thinking: [] },
  { type: 'optimizer', status: 'idle', output: '', thinking: [] },
  { type: 'tester', status: 'idle', output: '', thinking: [] }
];

interface PipelineStore extends PipelineState {
  taskId: string | null;
  isPaused: boolean;
  eventSource: EventSource | null;
  
  start: (description: string, type: string, model: string) => Promise<void>;
  pause: () => Promise<void>;
  resume: () => Promise<void>;
  cancel: () => Promise<void>;
  reset: () => void;
  importSuite: (suite: PromptSuite) => void;
  handleEvent: (event: any) => void;
  setTaskId: (taskId: string) => void;
  setEventSource: (eventSource: EventSource | null) => void;
}

export const usePipelineStore = create<PipelineStore>()((set, get) => ({
  currentStep: 0,
  steps: [...initialAgentStates],
  requirement: null,
  systemArchitecture: null,
  promptSuite: null,
  generatedPrompt: '',
  finalPrompt: '',
  review: null,
  testResult: null,
  isRunning: false,
  error: null,
  roleStates: [],
  currentRoleIndex: 0,
  totalRoles: 0,
  taskId: null,
  isPaused: false,
  eventSource: null,

  start: async (description, type, model) => {
    set({ 
      isRunning: true, 
      error: null, 
      isPaused: false,
      requirement: {
        type,
        targetModel: model,
        description,
        features: []
      }
    });
    
    try {
      const { taskId } = await startPipeline({ description, type, model });
      const eventSource = subscribePipelineEvents(taskId);
      
      eventSource.onmessage = (e) => {
        const data = JSON.parse(e.data);
        get().handleEvent(data);
      };
      
      eventSource.onerror = () => {
        set({ error: '连接断开', isRunning: false });
        eventSource.close();
      };
      
      set({ taskId, eventSource });
    } catch (error) {
      set({ error: error instanceof Error ? error.message : '启动失败', isRunning: false });
    }
  },

  pause: async () => {
    const { taskId } = get();
    if (taskId) {
      await pausePipeline(taskId);
      set({ isPaused: true });
    }
  },

  resume: async () => {
    const { taskId } = get();
    if (taskId) {
      await resumePipeline(taskId);
      set({ isPaused: false });
    }
  },

  cancel: async () => {
    const { taskId, eventSource } = get();
    if (taskId) {
      await cancelPipeline(taskId);
    }
    if (eventSource) {
      eventSource.close();
    }
    set({ isRunning: false, isPaused: false, eventSource: null });
  },

  reset: () => {
    const { eventSource } = get();
    if (eventSource) {
      eventSource.close();
    }
    set({
      currentStep: 0,
      steps: initialAgentStates.map(s => ({ ...s, status: 'idle', output: '', thinking: [] })),
      requirement: null,
      systemArchitecture: null,
      promptSuite: null,
      generatedPrompt: '',
      finalPrompt: '',
      review: null,
      testResult: null,
      isRunning: false,
      error: null,
      roleStates: [],
      currentRoleIndex: 0,
      totalRoles: 0,
      taskId: null,
      isPaused: false,
      eventSource: null
    });
  },

  importSuite: (suite) => {
    const roleStates: RoleProcessState[] = (suite.prompts || []).map(p => ({
      roleId: p.role_id,
      roleName: p.role_name,
      roleType: p.role_type,
      status: 'completed' as const,
      prompt: p.prompt,
      review: null,
      iterations: 0,
      finalScore: 0
    }));
    
    set({
      promptSuite: suite,
      roleStates,
      totalRoles: suite.total_roles || suite.prompts?.length || 0,
      finalPrompt: JSON.stringify(suite, null, 2),
      generatedPrompt: JSON.stringify(suite, null, 2)
    });
  },

  setTaskId: (taskId) => {
    set({ taskId, isRunning: true, isPaused: false, error: null });
  },

  setEventSource: (eventSource) => {
    set({ eventSource });
  },

  handleEvent: (event) => {
    const { type, data } = event;
    const steps = [...get().steps];
    
    switch (type) {
      case 'pipeline_started':
        set({ isRunning: true });
        break;
      
      case 'agent_started':
        const agentIndex = ['analyzer', 'generator', 'reviewer', 'optimizer', 'tester'].indexOf(data.agent);
        if (agentIndex >= 0) {
          steps[agentIndex] = { ...steps[agentIndex], status: 'running' };
          set({ steps, currentStep: agentIndex });
        }
        break;
      
      case 'agent_output':
        const outputIndex = ['analyzer', 'generator', 'reviewer', 'optimizer', 'tester'].indexOf(data.agent);
        if (outputIndex >= 0) {
          steps[outputIndex] = { ...steps[outputIndex], output: steps[outputIndex].output + (data.chunk || '') };
          set({ steps });
        }
        break;
      
      case 'agent_completed':
        const completeIndex = ['analyzer', 'generator', 'reviewer', 'optimizer', 'tester'].indexOf(data.agent);
        if (completeIndex >= 0) {
          steps[completeIndex] = { ...steps[completeIndex], status: data.success ? 'completed' : 'error' };
          set({ steps });
        }
        break;
      
      case 'role_state_updated':
        const roleStates = [...get().roleStates];
        if (roleStates[data.roleIndex]) {
          roleStates[data.roleIndex] = { ...roleStates[data.roleIndex], status: data.status };
          if (data.score !== undefined) {
            roleStates[data.roleIndex].finalScore = data.score;
          }
          set({ roleStates });
        }
        break;
      
      case 'pipeline_completed':
        set({ isRunning: false });
        get().eventSource?.close();
        break;
      
      case 'pipeline_error':
        set({ error: data.error, isRunning: false });
        get().eventSource?.close();
        break;
      
      case 'pipeline_paused':
        set({ isPaused: true });
        break;
      
      case 'pipeline_resumed':
        set({ isPaused: false });
        break;
      
      case 'pipeline_cancelled':
        set({ isRunning: false, isPaused: false });
        get().eventSource?.close();
        break;
    }
  }
}));
