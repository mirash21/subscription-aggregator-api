"""
🌊 Watermark System for Code Protection
"""
import hashlib
import os
from datetime import datetime
from typing import Dict

class CodeWatermarker:
    """Система водяных знаков для защиты кода"""
    
    # Уникальный идентификатор проекта
    PROJECT_SIGNATURE = "SUBSCRIPTION_API_PROTECTED_2026_MIRASH"
    
    @staticmethod
    def generate_file_watermark(filepath: str) -> str:
        """Генерация водяного знака для файла"""
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            # Создаем хеш содержимого + сигнатура проекта
            signature = CodeWatermarker.PROJECT_SIGNATURE
            watermark_data = f"{content.decode('utf-8', errors='ignore')}_{signature}_{filepath}"
            return hashlib.sha256(watermark_data.encode()).hexdigest()[:16]
        except:
            return "ERROR_WATERMARK"
    
    @staticmethod
    def verify_file_integrity(filepath: str, expected_watermark: str) -> bool:
        """Проверка целостности файла"""
        actual_watermark = CodeWatermarker.generate_file_watermark(filepath)
        return actual_watermark == expected_watermark
    
    @staticmethod
    def get_project_fingerprint() -> Dict[str, str]:
        """Получение цифрового отпечатка проекта"""
        return {
            "project_signature": CodeWatermarker.PROJECT_SIGNATURE,
            "generation_date": datetime.now().isoformat(),
            "protection_level": "COMMERCIAL_USE_RESTRICTED",
            "license_required": "YES",
            "contact": "legal@subscription-api.com"
        }
    
    @staticmethod
    def add_copyright_notice() -> str:
        """Добавление уведомления об авторских правах"""
        return f"""
/*
 * 🛡️ PROTECTED SOURCE CODE
 * Subscription Aggregator API v1.0
 * Copyright (c) 2026 Mirash21
 * 
 * This software is protected by AGPLv3 license with commercial use restrictions.
 * Unauthorized commercial distribution is strictly prohibited.
 * 
 * Installation ID: {hashlib.md5(os.getcwd().encode()).hexdigest()[:8]}
 * Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 * 
 * For licensing information: legal@subscription-api.com
 */
        """.strip()

# Глобальный экземпляр
watermarker = CodeWatermarker()