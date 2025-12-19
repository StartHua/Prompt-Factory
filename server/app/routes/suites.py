# -*- coding: utf-8 -*-
"""Suites API routes."""

from flask import Blueprint, request, jsonify
from app.services.storage_service import get_storage_service

bp = Blueprint('suites', __name__, url_prefix='/api')


@bp.route('/suites', methods=['GET'])
def list_suites():
    """List all saved suites."""
    try:
        storage = get_storage_service()
        suites = storage.list_suites()
        return jsonify({'success': True, 'data': suites})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/suites/<name>', methods=['GET'])
def get_suite(name: str):
    """Get suite details."""
    try:
        storage = get_storage_service()
        suite = storage.get_suite(name)
        if suite is None:
            return jsonify({'success': False, 'error': '套件不存在'}), 404
        return jsonify({'success': True, 'data': suite})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/save-suite', methods=['POST'])
def save_suite():
    """Save a prompt suite."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求数据无效'}), 400
        
        storage = get_storage_service()
        result = storage.save_suite(data)
        
        return jsonify({
            'success': True,
            'message': '提示词套件已保存',
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
