import sqlite3
import psycopg2
import os

def migrate_sqlite_to_postgres():
    print("🚀 Начинаем миграцию данных из SQLite в PostgreSQL")
    print("=" * 60)
    
    # 1. Подключение к SQLite (файл на хосте)
    print("📊 Подключаемся к SQLite...")
    sqlite_conn = sqlite3.connect('db.sqlite3')
    sqlite_conn.row_factory = sqlite3.Row  # Для доступа по именам колонок
    sqlite_cursor = sqlite_conn.cursor()
    
    # 2. Подключение к PostgreSQL (в контейнере)
    print("🐘 Подключаемся к PostgreSQL...")
    try:
        # Настройки должны совпадать с вашим .env файлом
        pg_conn = psycopg2.connect(
            host='localhost',        # Для Windows используем localhost
            port=5432,              # Порт, который проброшен из контейнера
            database='delivery_db',
            user='delivery_user',
            password='strong_password_here'  # ЗАМЕНИТЕ на ваш пароль из .env!
        )
        pg_cursor = pg_conn.cursor()
        print("✅ Подключение к PostgreSQL успешно")
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        print("Убедитесь, что:")
        print("1. Контейнер с PostgreSQL запущен")
        print("2. Порт 5432 проброшен на хост")
        print("3. Пароль правильный")
        return
    
    # 3. Получаем список таблиц
    print("\n📋 Получаем список таблиц...")
    sqlite_cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """)
    
    tables = [row[0] for row in sqlite_cursor.fetchall()]
    print(f"Найдено таблиц: {len(tables)}")
    print(f"Таблицы: {', '.join(tables)}")
    
    total_records = 0
    
    # 4. Мигрируем каждую таблицу
    for table in tables:
        print(f"\n📊 Обрабатываем таблицу: {table}")
        
        # Получаем данные из SQLite
        sqlite_cursor.execute(f"SELECT * FROM {table}")
        rows = sqlite_cursor.fetchall()
        
        if not rows:
            print(f"   ℹ️  Таблица пуста, пропускаем")
            continue
        
        # Получаем названия колонок
        column_names = [description[0] for description in sqlite_cursor.description]
        
        # Создаём INSERT запрос
        placeholders = ', '.join(['%s'] * len(column_names))
        columns = ', '.join(column_names)
        insert_query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        try:
            # Вставляем данные построчно
            inserted = 0
            for row in rows:
                # Конвертируем sqlite3.Row в tuple
                row_data = tuple(row)
                pg_cursor.execute(insert_query, row_data)
                inserted += 1
            
            pg_conn.commit()
            print(f"   ✅ Успешно перенесено {inserted} записей")
            total_records += inserted
            
            # Покажем пример данных (первые 2 записи)
            if inserted > 0:
                print(f"   Пример данных:")
                for i, col in enumerate(column_names[:3]):  # Первые 3 колонки
                    print(f"     {col}: {row[col][:50] if len(str(row[col])) > 50 else row[col]}")
        
        except Exception as e:
            pg_conn.rollback()
            print(f"   ❌ Ошибка при переносе: {e}")
            
            # Пробуем вставить без конфликтующих записей
            try:
                print("   🔄 Пробуем альтернативный метод...")
                for row in rows:
                    try:
                        row_data = tuple(row)
                        pg_cursor.execute(insert_query, row_data)
                    except:
                        continue  # Пропускаем проблемные строки
                
                pg_conn.commit()
                print(f"   ⚠️  Перенесено частично: {pg_cursor.rowcount} записей")
            except Exception as e2:
                print(f"   💥 Критическая ошибка: {e2}")
    
    # 5. Закрываем соединения
    sqlite_cursor.close()
    sqlite_conn.close()
    pg_cursor.close()
    pg_conn.close()
    
    print("\n" + "=" * 60)
    print(f"🎉 Миграция завершена!")
    print(f"📊 Всего перенесено записей: {total_records}")
    print("\n🔍 Проверьте данные в админке: http://localhost:8000/admin")

if __name__ == "__main__":
    migrate_sqlite_to_postgres()