# -*- coding: utf-8 -*-
"""Pipeline data models."""

from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime


@dataclass
class WorkflowStep:
    """Workflow step definition."""
    step: int
    role: str
    action: str
    next: List[str] = field(default_factory=list)
    condition: Optional[str] = None


@dataclass
class WorkflowInfo:
    """Workflow information."""
    description: str
    steps: List[WorkflowStep] = field(default_factory=list)


@dataclass
class QualityGate:
    """Quality gate definition."""
    gate: str
    role: str
    criteria: List[str] = field(default_factory=list)
    pass_action: str = ""
    fail_action: str = ""


@dataclass
class SharedContext:
    """Shared context for all roles."""
    description: str
    items: List[str] = field(default_factory=list)


@dataclass
class SystemRole:
    """System role definition."""
    id: str
    name: str
    type: Literal['core', 'quality', 'support']
    description: str
    responsibilities: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    triggers: List[str] = field(default_factory=list)
    priority: int = 1


@dataclass
class SystemArchitecture:
    """System architecture from Analyzer."""
    system_name: str
    system_description: str
    domain: str
    target_user: str
    use_cases: List[str] = field(default_factory=list)
    roles: List[SystemRole] = field(default_factory=list)
    workflow: Optional[WorkflowInfo] = None
    quality_gates: List[QualityGate] = field(default_factory=list)
    shared_context: Optional[SharedContext] = None


@dataclass
class RolePrompt:
    """Generated prompt for a role."""
    role_id: str
    role_name: str
    role_type: Literal['core', 'quality', 'support']
    description: str
    prompt: str
    input_template: str = ""
    output_format: str = ""
    triggers: List[str] = field(default_factory=list)
    collaborates_with: List[str] = field(default_factory=list)


@dataclass
class WeaknessItem:
    """Weakness item in review."""
    issue: str
    severity: str
    location: str
    impact: str = ""  # 添加 impact 字段


@dataclass
class SuggestionItem:
    """Suggestion item in review."""
    priority: str
    suggestion: str
    example: str = ""


@dataclass
class ReviewResult:
    """Review result from Reviewer."""
    score: float
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[WeaknessItem] = field(default_factory=list)
    suggestions: List[SuggestionItem] = field(default_factory=list)
    verdict: Optional[str] = None
    dimensions: Optional[Dict[str, Any]] = None
    role_id: Optional[str] = None
    role_name: Optional[str] = None


@dataclass
class RoleProcessState:
    """Processing state for a single role."""
    role_id: str
    role_name: str
    role_type: Literal['core', 'quality', 'support']
    status: Literal['pending', 'generating', 'reviewing', 'optimizing', 'completed', 'error'] = 'pending'
    prompt: str = ""
    review: Optional[ReviewResult] = None
    iterations: int = 0
    final_score: float = 0.0


@dataclass
class TestSummary:
    """Test summary."""
    total_tests: int
    passed: int
    failed: int
    warnings: int
    pass_rate: float
    verdict: str


@dataclass
class TestCase:
    """Single test case."""
    id: str
    category: str
    name: str
    input: str
    expected: str
    actual: str
    status: str
    notes: str = ""


@dataclass
class TestIssue:
    """Issue found during testing."""
    severity: str
    test_id: str
    description: str
    recommendation: str


@dataclass
class TestResult:
    """Test result from Tester."""
    summary: TestSummary
    test_cases: List[TestCase] = field(default_factory=list)
    issues_found: List[TestIssue] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class PromptSuite:
    """Complete prompt suite."""
    system_name: str
    total_roles: int
    prompts: List[RolePrompt] = field(default_factory=list)
    workflow_summary: str = ""
    integration_notes: str = ""


@dataclass
class PromptRequirement:
    """User's prompt requirement."""
    type: str
    target_model: str
    description: str
    features: List[str] = field(default_factory=list)
    target_user: Optional[str] = None


@dataclass
class PipelineState:
    """Pipeline execution state."""
    task_id: str
    status: Literal['idle', 'running', 'paused', 'completed', 'error', 'cancelled'] = 'idle'
    current_step: int = 0
    description: str = ""
    prompt_type: str = ""
    model: str = ""
    system_architecture: Optional[SystemArchitecture] = None
    prompt_suite: Optional[PromptSuite] = None
    role_states: List[RoleProcessState] = field(default_factory=list)
    review: Optional[ReviewResult] = None
    test_result: Optional[TestResult] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class PipelineEvent:
    """SSE event for pipeline progress."""
    type: Literal[
        'pipeline_started',
        'agent_started',
        'agent_output',
        'agent_completed',
        'role_state_updated',
        'pipeline_completed',
        'pipeline_error',
        'pipeline_paused',
        'pipeline_resumed',
        'pipeline_cancelled'
    ]
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
