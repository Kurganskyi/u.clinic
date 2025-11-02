#!/usr/bin/env python
"""
Скрипт для запуска тестов
"""
import subprocess
import sys


def main():
    """Запуск pytest"""
    try:
        result = subprocess.run(
            ['py', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
            check=False
        )
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("Ошибка: pytest не установлен. Установите: pip install pytest pytest-asyncio pytest-mock")
        sys.exit(1)


if __name__ == "__main__":
    main()

