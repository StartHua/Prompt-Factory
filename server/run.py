#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Flask application entry point."""

from app import create_app

app = create_app()

if __name__ == '__main__':
    # 使用 use_reloader=False 可以避免文件变化导致重启中断任务
    # 生产环境建议设置 debug=False
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    use_reloader = os.environ.get('FLASK_RELOADER', 'false').lower() == 'true'
    
    app.run(
        host='0.0.0.0', 
        port=5000, 
        debug=debug_mode,
        use_reloader=use_reloader  # 默认关闭自动重载，避免中断任务
    )
