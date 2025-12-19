# -*- coding: utf-8 -*-
"""Flask application factory."""

from flask import Flask
from flask_cors import CORS

def create_app(config_name: str = 'default') -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    from app.routes import pipeline, settings, suites, history
    app.register_blueprint(pipeline.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(suites.bp)
    app.register_blueprint(history.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app: Flask) -> None:
    """Register global error handlers."""
    from flask import jsonify
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'success': False, 'error': str(error.description)}), 400
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'success': False, 'error': '资源不存在'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'success': False, 'error': '服务器内部错误'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        return jsonify({'success': False, 'error': str(error)}), 500
