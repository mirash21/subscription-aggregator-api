#!/usr/bin/env python3
"""
🔐 Commercial License Generator
Скрипт для генерации коммерческих лицензий
"""
import json
import hashlib
import argparse
from datetime import datetime, timedelta
import secrets

def generate_license(installation_id: str, license_type: str = "commercial", duration_days: int = 365) -> dict:
    """Генерация коммерческой лицензии"""
    
    expiry_date = datetime.now() + timedelta(days=duration_days)
    
    license_data = {
        "installation_id": installation_id,
        "license_type": license_type,
        "issued_date": datetime.now().isoformat(),
        "expiry": expiry_date.isoformat(),
        "company": "LICENSED_COMPANY",
        "contact": "license@subscription-api.com",
        "features": ["full_api_access", "production_use", "support_included"]
    }
    
    # Создание цифровой подписи
    data_to_sign = f"{installation_id}_{expiry_date.isoformat()}_{license_type}"
    signature = hashlib.sha256(data_to_sign.encode()).hexdigest()
    license_data["signature"] = signature
    
    return license_data

def save_license(license_data: dict, filename: str = "commercial_license.key"):
    """Сохранение лицензии в файл"""
    with open(filename, 'w') as f:
        json.dump(license_data, f, indent=2)
    print(f"✅ License saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="Generate commercial license")
    parser.add_argument("--installation-id", required=True, help="Installation ID")
    parser.add_argument("--type", default="commercial", help="License type")
    parser.add_argument("--days", type=int, default=365, help="License duration in days")
    parser.add_argument("--output", default="commercial_license.key", help="Output filename")
    
    args = parser.parse_args()
    
    print("🔐 Generating commercial license...")
    print(f"Installation ID: {args.installation_id}")
    print(f"License type: {args.type}")
    print(f"Duration: {args.days} days")
    
    license_data = generate_license(args.installation_id, args.type, args.days)
    save_license(license_data, args.output)
    
    print("\n📋 License details:")
    print(f"  Type: {license_data['license_type']}")
    print(f"  Expiry: {license_data['expiry']}")
    print(f"  Signature: {license_data['signature'][:16]}...")

if __name__ == "__main__":
    main()