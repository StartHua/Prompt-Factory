# -*- coding: utf-8 -*-
"""Settings API routes."""

from flask import Blueprint, request, jsonify
from app.services.storage_service import get_storage_service
from app.models.settings import Settings

bp = Blueprint('settings', __name__, url_prefix='/api')


@bp.route('/settings', methods=['GET'])
def get_settings():
    """Get current settings."""
    try:
        storage = get_storage_service()
        settings = storage.load_settings()
        return jsonify({'success': True, 'data': settings.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/settings', methods=['POST'])
def save_settings():
    """Save settings."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据无效'}), 400
        
        settings = Settings.from_dict(data)
        storage = get_storage_service()
        storage.save_settings(settings)
        
        return jsonify({'success': True, 'message': '配置已保存'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
