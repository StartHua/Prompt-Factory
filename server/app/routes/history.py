# -*- coding: utf-8 -*-
"""History API routes."""

from datetime import datetime
from flask import Blueprint, request, jsonify
from app.services.storage_service import get_storage_service
from app.models.history import HistoryRecord

bp = Blueprint('history', __name__, url_prefix='/api')


@bp.route('/history', methods=['GET'])
def get_history():
    """Get history records."""
    try:
        storage = get_storage_service()
        records = storage.get_history(limit=50)
        return jsonify({'success': True, 'data': [r.to_dict() for r in records]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/history', methods=['POST'])
def add_history():
    """Add a history record."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据无效'}), 400
        
        record = HistoryRecord(
            id=str(int(datetime.now().timestamp() * 1000)),
            description=data.get('description', ''),
            type=data.get('type', ''),
            system_name=data.get('systemName', ''),
            roles_count=data.get('rolesCount', 0),
            score=data.get('score', 0.0),
            folder_name=data.get('folderName')
        )
        
        storage = get_storage_service()
        saved = storage.add_history(record)
        
        return jsonify({'success': True, 'data': saved.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/history/<id>', methods=['DELETE'])
def delete_history(id: str):
    """Delete a history record."""
    try:
        storage = get_storage_service()
        storage.delete_history(id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/history', methods=['DELETE'])
def clear_history():
    """Clear all history records."""
    try:
        storage = get_storage_service()
        storage.clear_history()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
