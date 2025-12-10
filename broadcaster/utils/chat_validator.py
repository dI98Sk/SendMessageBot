"""
Утилита для валидации и фильтрации chat_id
"""
from typing import List, Tuple

def validate_chat_id(chat_id: int) -> Tuple[bool, str]:
    """
    Валидация одного chat_id
    
    Args:
        chat_id: ID чата для проверки
        
    Returns:
        tuple[bool, str]: (валиден ли, причина если невалиден)
    """
    # Проверка типа
    if not isinstance(chat_id, int):
        return False, f"Не является числом (тип: {type(chat_id).__name__})"
    
    # Проверка что это не положительное число (для групп/каналов)
    if chat_id > 0:
        return False, "Положительный ID (группы/каналы должны иметь отрицательный ID, начинающийся с -100)"
    
    # Проверка формата для супергрупп/каналов (обычно начинаются с -100)
    # Telegram chat_id могут быть до 19 цифр, так что проверяем только минимальную длину
    # Максимальная длина не ограничиваем, так как Telegram может использовать длинные ID
    
    # Проверка минимальной длины (старые группы могут быть короче)
    if abs(chat_id) < 1000000:
        # Это может быть старая группа, но предупредим
        return True, "warning: Короткий ID, возможно старая группа"
    
    return True, "OK"

def filter_valid_chat_ids(chat_ids: List[int], remove_invalid: bool = True) -> Tuple[List[int], List[Tuple[int, str]]]:
    """
    Фильтрация списка chat_id, удаление невалидных
    
    Args:
        chat_ids: Список chat_id для проверки
        remove_invalid: Удалять невалидные ID из результата
        
    Returns:
        tuple[List[int], List[Tuple[int, str]]]: (валидные ID, список невалидных с причинами)
    """
    valid_ids = []
    invalid_ids = []
    
    for chat_id in chat_ids:
        is_valid, reason = validate_chat_id(chat_id)
        
        if is_valid:
            if "warning" not in reason.lower():
                valid_ids.append(chat_id)
            else:
                # Предупреждение, но добавляем
                valid_ids.append(chat_id)
                invalid_ids.append((chat_id, reason))
        else:
            invalid_ids.append((chat_id, reason))
            if not remove_invalid:
                # Если не удаляем, все равно добавляем (но с предупреждением)
                valid_ids.append(chat_id)
    
    return valid_ids, invalid_ids

def validate_targets_list(targets: List[int], list_name: str = "targets", verbose: bool = True) -> Tuple[List[int], List[Tuple[int, str]]]:
    """
    Валидация и фильтрация списка целей
    
    Args:
        targets: Список chat_id
        list_name: Имя списка для логирования
        verbose: Выводить предупреждения в консоль
        
    Returns:
        tuple[List[int], List[Tuple[int, str]]]: (отфильтрованный список, список невалидных с причинами)
    """
    if not targets:
        return [], []
    
    valid_ids, invalid_ids = filter_valid_chat_ids(targets, remove_invalid=True)
    removed_count = len(invalid_ids)
    
    if invalid_ids and verbose:
        print(f"⚠️  В списке '{list_name}' найдено {removed_count} невалидных chat_id:")
        for chat_id, reason in invalid_ids[:10]:  # Показываем первые 10
            print(f"   • {chat_id}: {reason}")
        if len(invalid_ids) > 10:
            print(f"   ... и еще {len(invalid_ids) - 10} невалидных ID")
    
    return valid_ids, invalid_ids

