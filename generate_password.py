#!/usr/bin/env python3
"""
Генератор безопасного мастер-пароля
"""
import secrets
import string

def generate_master_password(length=32):
    """Генерация безопасного мастер-пароля"""
    # Используем буквы, цифры и специальные символы
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    
    # Генерируем пароль
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password

def generate_readable_password(length=24):
    """Генерация читаемого пароля (без специальных символов)"""
    # Используем только буквы и цифры
    characters = string.ascii_letters + string.digits
    
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password

def main():
    print("🔐 Генератор мастер-пароля для SendMessageBot")
    print("=" * 50)
    
    print("\nВарианты паролей:")
    
    # Вариант 1: Максимально безопасный
    secure_password = generate_master_password(32)
    print(f"\n1. Максимально безопасный (32 символа):")
    print(f"   {secure_password}")
    
    # Вариант 2: Читаемый
    readable_password = generate_readable_password(24)
    print(f"\n2. Читаемый (24 символа):")
    print(f"   {readable_password}")
    
    # Вариант 3: Средний
    medium_password = generate_master_password(20)
    print(f"\n3. Средний уровень (20 символов):")
    print(f"   {medium_password}")
    
    print("\n" + "=" * 50)
    print("📋 Рекомендации:")
    print("• Сохраните пароль в безопасном месте (менеджер паролей)")
    print("• НЕ добавляйте пароль в git или другие системы контроля версий")
    print("• Используйте первый вариант для максимальной безопасности")
    print("• Если забудете пароль, данные нельзя будет расшифровать!")
    
    print("\n💡 Совет:")
    print("Можете использовать любой из предложенных паролей")
    print("или создать свой собственный (минимум 16 символов)")

if __name__ == "__main__":
    main()
