"""
🛡️ License Management System for Commercial Use Protection
"""
import os
import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class LicenseManager:
    """Управление лицензиями и защита от несанкционированного использования"""
    
    def __init__(self):
        self.license_file = ".license.key"
        self.installation_id = self._get_installation_id()
        self.is_development = self._check_development_mode()
        
    def _get_installation_id(self) -> str:
        """Генерация уникального ID установки"""
        # Используем hardware ID + путь к проекту
        machine_id = self._get_machine_id()
        project_path = os.getcwd()
        combined = f"{machine_id}_{project_path}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def _get_machine_id(self) -> str:
        """Получение ID машины"""
        try:
            import platform
            # Комбинируем различные идентификаторы системы
            identifiers = [
                platform.node(),
                platform.machine(),
                platform.processor()
            ]
            return hashlib.md5("".join(identifiers).encode()).hexdigest()
        except:
            return str(uuid.uuid4())
    
    def _check_development_mode(self) -> bool:
        """Проверка режима разработки"""
        dev_indicators = [
            'DEBUG' in os.environ,
            'development' in os.getcwd().lower(),
            '.git' in os.listdir('.'),
            'venv' in os.listdir('.') or 'env' in os.listdir('.')
        ]
        return any(dev_indicators)
    
    def validate_usage(self) -> Tuple[bool, str]:
        """Валидация использования - основная точка защиты"""
        # В режиме разработки разрешаем использование
        if self.is_development:
            logger.info("Development mode detected - usage allowed")
            return True, "Development mode"
        
        # Проверяем наличие валидной лицензии
        if self._has_valid_license():
            return True, "Valid commercial license"
        
        # Проверяем условия бесплатного использования
        if self._is_free_usage_allowed():
            return True, "Free usage conditions met"
        
        # Если ничего не подошло - блокируем
        return False, "Commercial license required"
    
    def _has_valid_license(self) -> bool:
        """Проверка наличия валидной коммерческой лицензии"""
        try:
            if not os.path.exists(self.license_file):
                return False
                
            with open(self.license_file, 'r') as f:
                license_data = json.load(f)
            
            # Проверяем подпись и срок действия
            if self._verify_license_signature(license_data):
                expiry_date = datetime.fromisoformat(license_data['expiry'])
                return datetime.now() < expiry_date
            
            return False
        except Exception as e:
            logger.warning(f"License validation error: {e}")
            return False
    
    def _verify_license_signature(self, license_data: Dict) -> bool:
        """Верификация подписи лицензии"""
        try:
            # Проверяем контрольную сумму
            expected_hash = license_data.get('signature')
            data_to_hash = f"{license_data['installation_id']}_{license_data['expiry']}_{license_data['license_type']}"
            actual_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
            
            return expected_hash == actual_hash and license_data['installation_id'] == self.installation_id
        except:
            return False
    
    def _is_free_usage_allowed(self) -> bool:
        """Проверка условий бесплатного использования"""
        # Проверяем ограничения по времени использования
        first_run_file = ".first_run"
        
        if not os.path.exists(first_run_file):
            # Первый запуск - сохраняем время
            with open(first_run_file, 'w') as f:
                json.dump({"first_run": datetime.now().isoformat()}, f)
            return True
        
        # Проверяем срок пробного периода (30 дней)
        try:
            with open(first_run_file, 'r') as f:
                data = json.load(f)
            first_run = datetime.fromisoformat(data['first_run'])
            trial_period = timedelta(days=30)
            
            return datetime.now() < (first_run + trial_period)
        except:
            return True  # Если ошибка - разрешаем
    
    def get_license_info(self) -> Dict:
        """Получение информации о текущей лицензии"""
        is_valid, reason = self.validate_usage()
        
        return {
            "valid": is_valid,
            "reason": reason,
            "installation_id": self.installation_id,
            "development_mode": self.is_development,
            "trial_active": self._is_trial_active()
        }
    
    def _is_trial_active(self) -> bool:
        """Проверка активности пробного периода"""
        if self.is_development:
            return False
            
        first_run_file = ".first_run"
        if not os.path.exists(first_run_file):
            return True
            
        try:
            with open(first_run_file, 'r') as f:
                data = json.load(f)
            first_run = datetime.fromisoformat(data['first_run'])
            trial_end = first_run + timedelta(days=30)
            return datetime.now() < trial_end
        except:
            return True

# Глобальный экземпляр менеджера лицензий
license_manager = LicenseManager()

def enforce_license():
    """Декоратор для защиты функций лицензией"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            is_valid, reason = license_manager.validate_usage()
            if not is_valid:
                raise PermissionError(f"License violation: {reason}. Commercial use requires paid license.")
            return func(*args, **kwargs)
        return wrapper
    return decorator