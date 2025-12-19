# -*- coding: utf-8 -*-
"""Pipeline API routes."""

import json
import threading
from datetime import datetime
from flask import Blueprint, request, jsonify, Response, g
from typing import Optional

from app.services.pipeline_service import PipelineService
from app.services.llm_client import LLMClient
from app.services.storage_service import get_storage_service
from app.services.prompt_loader import set_language

bp = Blueprint('pipeline', __name__, url_prefix='/api/pipeline')


def log(msg: str, level: str = "INFO"):
    """打印带时间戳的日志"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] [Route] [{level}] {msg}", flush=True)

# Store active pipelines
_pipelines: dict = {}
_pipeline_lock = threading.Lock()


def get_pipeline(task_id: str) -> Optional[PipelineService]:
    """Get pipeline by task ID."""
    with _pipeline_lock:
        return _pipelines.get(task_id)


@bp.route('/start', methods=['POST'])
def start_pipeline():
    """Start a new pipeline execution."""
    log("收到 /start 请求")
    data = request.get_json()
    if not data:
        log("请求数据无效", "ERROR")
        return jsonify({'success': False, 'error': '请求数据无效'}), 400
    
    description = data.get('description', '').strip()
    prompt_type = data.get('type', 'general')
    model = data.get('model', 'claude-sonnet-4-5-20251022')
    
    log(f"参数: type={prompt_type}, model={model}, description={description[:50]}...")
    
    if not description:
        log("需求描述为空", "ERROR")
        return jsonify({'success': False, 'error': '请输入需求描述'}), 400
    
    # Get settings for API key
    log("加载配置...")
    storage = get_storage_service()
    settings = storage.load_settings()
    
    log(f"配置内容: api_key={settings.api_key[:10] if settings.api_key else 'None'}..., base_url={settings.base_url}")
    
    if not settings.api_key:
        log("API Key 未配置", "ERROR")
        return jsonify({'success': False, 'error': '请先配置 API Key'}), 400
    
    log(f"配置加载成功: base_url={settings.base_url}")
    
    # Create LLM client and pipeline
    use_stream = settings.use_stream
    log(f"使用流式输出: {use_stream}")
    
    # 设置语言
    language = settings.language or 'cn'
    set_language(language)
    log(f"使用语言: {language}")
    
    # 是否启用并行执行
    use_parallel = data.get('parallel', True)
    max_parallel = data.get('maxParallel', 3)
    
    llm_client = LLMClient(api_key=settings.api_key, base_url=settings.base_url)
    pipeline = PipelineService(llm_client, use_stream=use_stream, max_parallel=max_parallel)
    task_id = pipeline.start(description, prompt_type, model)
    
    with _pipeline_lock:
        _pipelines[task_id] = pipeline
    
    log(f"流水线创建成功: task_id={task_id}, parallel={use_parallel}, max_parallel={max_parallel}")
    
    # Start pipeline in background thread
    def run_pipeline():
        log("后台线程启动")
        try:
            suite = pipeline.run_full_pipeline(parallel=use_parallel)
            
            if suite:
                log("流水线执行完成 ✓")
                pipeline._emit_event('pipeline_completed', {'suite': suite.system_name})
            else:
                log("流水线执行失败", "ERROR")
                pipeline._emit_event('pipeline_error', {'error': '流水线执行失败'})
        except Exception as e:
            log(f"流水线执行异常: {type(e).__name__}: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            if pipeline.state:
                pipeline.state.status = 'error'
                pipeline.state.error = str(e)
            pipeline._emit_event('pipeline_error', {'error': str(e)})
    
    thread = threading.Thread(target=run_pipeline, daemon=True)
    thread.start()
    log("后台线程已启动")
    
    return jsonify({'success': True, 'data': {'taskId': task_id}})


@bp.route('/stream')
def stream_events():
    """SSE endpoint for pipeline progress."""
    task_id = request.args.get('taskId')
    if not task_id:
        return jsonify({'success': False, 'error': '缺少 taskId'}), 400
    
    pipeline = get_pipeline(task_id)
    if not pipeline:
        return jsonify({'success': False, 'error': '任务不存在'}), 404
    
    def generate():
        yield f'data: {json.dumps({"type": "connected"})}\n\n'
        
        while True:
            try:
                event = pipeline.event_queue.get(timeout=30)
                yield f'data: {json.dumps({"type": event.type, "data": event.data, "timestamp": event.timestamp})}\n\n'
                
                if event.type in ('pipeline_completed', 'pipeline_error', 'pipeline_cancelled'):
                    break
            except:
                yield f'data: {json.dumps({"type": "heartbeat"})}\n\n'
    
    return Response(generate(), mimetype='text/event-stream')


@bp.route('/pause', methods=['POST'])
def pause_pipeline():
    """Pause pipeline execution."""
    data = request.get_json() or {}
    task_id = data.get('taskId')
    pipeline = get_pipeline(task_id) if task_id else None
    if pipeline:
        pipeline.pause()
    return jsonify({'success': True})


@bp.route('/resume', methods=['POST'])
def resume_pipeline():
    """Resume pipeline execution."""
    data = request.get_json() or {}
    task_id = data.get('taskId')
    pipeline = get_pipeline(task_id) if task_id else None
    if pipeline:
        pipeline.resume()
    return jsonify({'success': True})


@bp.route('/cancel', methods=['POST'])
def cancel_pipeline():
    """Cancel pipeline execution."""
    data = request.get_json() or {}
    task_id = data.get('taskId')
    pipeline = get_pipeline(task_id) if task_id else None
    if pipeline:
        pipeline.cancel()
    return jsonify({'success': True})


@bp.route('/incomplete', methods=['GET'])
def list_incomplete_tasks():
    """List all incomplete tasks that can be resumed (断点恢复列表)."""
    log("查询未完成任务列表")
    storage = get_storage_service()
    tasks = storage.list_incomplete_tasks()
    return jsonify({'success': True, 'data': tasks})


@bp.route('/recover', methods=['POST'])
def recover_pipeline():
    """Resume an incomplete task (断点恢复执行)."""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '请求数据无效'}), 400
    
    task_id = data.get('taskId')
    if not task_id:
        return jsonify({'success': False, 'error': '缺少 taskId'}), 400
    
    log(f"恢复任务: {task_id}")
    
    # Get settings
    storage = get_storage_service()
    settings = storage.load_settings()
    
    if not settings.api_key:
        return jsonify({'success': False, 'error': '请先配置 API Key'}), 400
    
    # 设置语言
    language = settings.language or 'cn'
    set_language(language)
    log(f"使用语言: {language}")
    
    # Check if task exists
    progress = storage.load_task_progress(task_id)
    if not progress:
        return jsonify({'success': False, 'error': '任务不存在或已完成'}), 404
    
    use_parallel = data.get('parallel', True)
    
    # Create pipeline and resume
    llm_client = LLMClient(api_key=settings.api_key, base_url=settings.base_url)
    pipeline = PipelineService(llm_client, use_stream=settings.use_stream)
    
    with _pipeline_lock:
        _pipelines[task_id] = pipeline
    
    def run_recovery():
        log(f"开始恢复任务: {task_id}")
        try:
            suite = pipeline.resume_pipeline(task_id, parallel=use_parallel)
            
            if suite:
                log("任务恢复执行完成 ✓")
                pipeline._emit_event('pipeline_completed', {'suite': suite.system_name})
            else:
                log("任务恢复执行失败", "ERROR")
                pipeline._emit_event('pipeline_error', {'error': '恢复执行失败'})
        except Exception as e:
            log(f"任务恢复异常: {type(e).__name__}: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            if pipeline.state:
                pipeline.state.status = 'error'
                pipeline.state.error = str(e)
            pipeline._emit_event('pipeline_error', {'error': str(e)})
    
    thread = threading.Thread(target=run_recovery, daemon=True)
    thread.start()
    
    return jsonify({'success': True, 'data': {'taskId': task_id, 'resumed': True}})
