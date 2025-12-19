export type AgentType = 'analyzer' | 'generator' | 'reviewer' | 'optimizer' | 'tester';
export type AgentStatus = 'idle' | 'running' | 'completed' | 'error';

export interface AgentState {
  type: AgentType;
  status: AgentStatus;
  output: string;
  thinking: string[];
}

export interface ReviewResult {
  score: number;
  strengths: string[];
  weaknesses: Array<{ issue: string; severity: string; location: string }> | string[];
  suggestions: Array<{ priority: string; suggestion: string; example?: string }> | string[];
  verdict?: string;
}

export interface TestResult {
  summary: {
    total_tests: number;
    passed: number;
    failed: number;
    warnings: number;
    pass_rate: number;
    verdict: string;
  };
  test_cases: Array<{
    id: string;
    category: string;
    name: string;
    input: string;
    expected: string;
    actual: string;
    status: string;
    notes: string;
  }>;
  issues_found: Array<{
    severity: string;
    test_id: string;
    description: string;
    recommendation: string;
  }>;
  recommendations: string[];
}

export interface SystemRole {
  id: string;
  name: string;
  type: 'core' | 'quality' | 'support';
  description: string;
  responsibilities: string[];
  inputs: string[];
  outputs: string[];
  triggers: string[];
  priority: number;
}

export interface SystemArchitecture {
  system_name: string;
  system_description: string;
  domain: string;
  target_user: string;
  use_cases: string[];
  roles: SystemRole[];
}


export interface RolePrompt {
  role_id: string;
  role_name: string;
  role_type: 'core' | 'quality' | 'support';
  description: string;
  prompt: string;
  input_template: string;
  output_format: string;
  triggers: string[];
}

export interface PromptSuite {
  system_name: string;
  total_roles: number;
  prompts: RolePrompt[];
  workflow_summary: string;
  integration_notes: string;
}

export interface RoleProcessState {
  roleId: string;
  roleName: string;
  roleType: 'core' | 'quality' | 'support';
  status: 'pending' | 'generating' | 'reviewing' | 'optimizing' | 'completed' | 'error';
  prompt: string;
  review: ReviewResult | null;
  iterations: number;
  finalScore: number;
}

export interface PromptRequirement {
  type: string;
  targetModel: string;
  description: string;
  features: string[];
  target_user?: string;
}

export interface PipelineState {
  currentStep: number;
  steps: AgentState[];
  requirement: PromptRequirement | null;
  systemArchitecture: SystemArchitecture | null;
  promptSuite: PromptSuite | null;
  generatedPrompt: string;
  finalPrompt: string;
  review: ReviewResult | null;
  testResult: TestResult | null;
  isRunning: boolean;
  error: string | null;
  roleStates: RoleProcessState[];
  currentRoleIndex: number;
  totalRoles: number;
}

export type Language = 'cn' | 'en';

export interface Settings {
  apiKey: string;
  baseUrl: string;
  defaultModel: string;
  useStream: boolean;
  language: Language;
}

export interface HistoryRecord {
  id: string;
  description: string;
  type: string;
  systemName: string;
  rolesCount: number;
  score: number;
  createdAt: string;
  folderName?: string;
}

export interface SuiteListItem {
  name: string;
  systemName?: string;
  description?: string;
  score?: number;
  rolesCount?: number;
  savedAt?: string;
}
