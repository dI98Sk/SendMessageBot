#!/usr/bin/env python3
"""
Скрипт для валидации chat_id в списках целей
"""
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.targets import TARGETS, TEST_TARGETS, ADS_TARGET, PRICE_TARGET, TEST_TARGETS_ADS, B2C_TARGET
from utils.chat_validator import validate_targets_list

def main():
    print("🔍 Проверка валидности chat_id в списках целей\n")
    print("=" * 60)
    
    lists_to_check = [
        ("TARGETS", TARGETS),
        ("TEST_TARGETS", TEST_TARGETS),
        ("ADS_TARGET", ADS_TARGET),
        ("PRICE_TARGET", PRICE_TARGET),
        ("TEST_TARGETS_ADS", TEST_TARGETS_ADS),
        ("B2C_TARGET", B2C_TARGET),
    ]
    
    total_invalid = 0
    
    for list_name, targets in lists_to_check:
        if not targets:
            print(f"📋 {list_name}: пустой список")
            continue
        
        valid_ids, invalid_ids = validate_targets_list(targets, list_name)
        removed_count = len(invalid_ids)
        total_invalid += removed_count
        
        print(f"\n📋 {list_name}:")
        print(f"   Всего ID: {len(targets)}")
        print(f"   Валидных: {len(valid_ids)}")
        print(f"   Невалидных: {removed_count}")
        
        if invalid_ids:
            print(f"\n   ❌ Невалидные ID:")
            for chat_id, reason in invalid_ids[:20]:  # Показываем первые 20
                print(f"      • {chat_id}: {reason}")
            if len(invalid_ids) > 20:
                print(f"      ... и еще {len(invalid_ids) - 20} невалидных ID")
    
    print("\n" + "=" * 60)
    print(f"📊 Итого: найдено {total_invalid} невалидных chat_id")
    
    if total_invalid > 0:
        print("\n⚠️  Рекомендации:")
        print("   1. Удалите невалидные ID из config/targets.py")
        print("   2. Проверьте, что все ID отрицательные (начинаются с -100)")
        print("   3. Убедитесь, что это ID групп/каналов, а не пользователей")
        return 1
    else:
        print("\n✅ Все chat_id валидны!")
        return 0

if __name__ == "__main__":
    sys.exit(main())

