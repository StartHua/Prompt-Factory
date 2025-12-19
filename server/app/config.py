# -*- coding: utf-8 -*-
"""Application configuration."""

import os
from pathlib import Path

class Config:
    """Base configuration."""
    
    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    CONFIG_DIR = BASE_DIR / 'config'
    RESULT_DIR = BASE_DIR / 'result'
    PROMPTS_DIR = BASE_DIR / 'prompts'
    
    # Encryption
    ENCRYPTION_KEY = os.environ.get('CONFIG_KEY', 'prompt-factory-secret-key-32ch')
    
    # Pipeline settings
    MAX_ITERATIONS = 3
    PASS_SCORE = 8.0
    DEFAULT_MAX_PARALLEL = 3
    
    # History settings
    MAX_HISTORY_RECORDS = 50
    
    # Ensure directories exist
    @classmethod
    def init_app(cls):
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        cls.RESULT_DIR.mkdir(parents=True, exist_ok=True)

# Initialize directories on import
Config.init_app()
