#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Веб-приложение для управления информацией о преподавателях
Flask бэкенд с SQLite базой данных
"""

import sqlite3
import json
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Путь к базе данных
DB_PATH = 'teachers.db'

# ==================== ИНИЦИАЛИЗАЦИЯ БД ====================

def init_db():
    """Инициализирует базу данных с таблицами"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица кафедр
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            head TEXT,
            phone TEXT
        )
    ''')
    
    # Таблица преподавателей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            patronymic TEXT,
            department_id INTEGER NOT NULL,
            position TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            academic_degree TEXT,
            academic_title TEXT,
            hire_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
    ''')
    
    # Таблица публикаций
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS publications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            publication_date TEXT,
            journal TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
        )
    ''')
    
    # Таблица повышения квалификации
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS professional_development (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            course_name TEXT NOT NULL,
            completion_date TEXT,
            certificate TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
        )
    ''')
    
    # Таблица наград
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER NOT NULL,
            award_name TEXT NOT NULL,
            award_date TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def load_initial_data():
    """Загружает начальные данные если база пуста"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Проверяем, есть ли уже данные
    cursor.execute('SELECT COUNT(*) FROM teachers')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Добавляем кафедры
    departments = [
        ('Информатика', 'Петров И.И.', '+7-999-111-11-11'),
        ('Математика', 'Иванов В.В.', '+7-999-222-22-22'),
        ('Физика', 'Сидоров А.А.', '+7-999-333-33-33'),
        ('Литература', 'Смирнова О.О.', '+7-999-444-44-44'),
    ]
    
    cursor.executemany(
        'INSERT INTO departments (name, head, phone) VALUES (?, ?, ?)',
        departments
    )
    
    # Получаем ID кафедр
    cursor.execute('SELECT id, name FROM departments')
    dept_map = {row[1]: row[0] for row in cursor.fetchall()}
    
    # Добавляем преподавателей
    teachers_data = [
        # Информатика
        ('Александр', 'Петров', 'Сергеевич', dept_map['Информатика'], 'Доцент', 'a.petrov@univ.ru', '+7-999-111-11-01', 'Кандидат наук', 'Доцент', '2010-09-01'),
        ('Мария', 'Иванова', 'Ивановна', dept_map['Информатика'], 'Профессор', 'm.ivanova@univ.ru', '+7-999-111-11-02', 'Доктор наук', 'Профессор', '2005-09-01'),
        ('Сергей', 'Сидоров', 'Николаевич', dept_map['Информатика'], 'Ассистент', 's.sidorov@univ.ru', '+7-999-111-11-03', 'Магистр', '', '2018-09-01'),
        ('Елена', 'Смирнова', 'Владимировна', dept_map['Информатика'], 'Старший преподаватель', 'e.smirnova@univ.ru', '+7-999-111-11-04', 'Кандидат наук', '', '2012-09-01'),
        ('Дмитрий', 'Кузнецов', 'Алексеевич', dept_map['Информатика'], 'Лектор', 'd.kuznetsov@univ.ru', '+7-999-111-11-05', 'Магистр', '', '2015-09-01'),
        
        # Математика
        ('Виктор', 'Морозов', 'Викторович', dept_map['Математика'], 'Профессор', 'v.morozov@univ.ru', '+7-999-222-22-01', 'Доктор наук', 'Профессор', '2000-09-01'),
        ('Ольга', 'Волкова', 'Сергеевна', dept_map['Математика'], 'Доцент', 'o.volkova@univ.ru', '+7-999-222-22-02', 'Кандидат наук', 'Доцент', '2008-09-01'),
        ('Павел', 'Соколов', 'Павлович', dept_map['Математика'], 'Старший преподаватель', 'p.sokolov@univ.ru', '+7-999-222-22-03', 'Кандидат наук', '', '2011-09-01'),
        ('Анна', 'Лебедева', 'Ивановна', dept_map['Математика'], 'Ассистент', 'a.lebedeva@univ.ru', '+7-999-222-22-04', 'Магистр', '', '2019-09-01'),
        ('Игорь', 'Орлов', 'Игоревич', dept_map['Математика'], 'Лектор', 'i.orlov@univ.ru', '+7-999-222-22-05', 'Магистр', '', '2016-09-01'),
        
        # Физика
        ('Владимир', 'Громов', 'Владимирович', dept_map['Физика'], 'Профессор', 'v.gromov@univ.ru', '+7-999-333-33-01', 'Доктор наук', 'Профессор', '2002-09-01'),
        ('Ирина', 'Звездина', 'Ивановна', dept_map['Физика'], 'Доцент', 'i.zvezdina@univ.ru', '+7-999-333-33-02', 'Кандидат наук', 'Доцент', '2009-09-01'),
        ('Константин', 'Лучистов', 'Константинович', dept_map['Физика'], 'Старший преподаватель', 'k.luchistov@univ.ru', '+7-999-333-33-03', 'Кандидат наук', '', '2013-09-01'),
        ('Наталья', 'Энергина', 'Сергеевна', dept_map['Физика'], 'Ассистент', 'n.energina@univ.ru', '+7-999-333-33-04', 'Магистр', '', '2020-09-01'),
        ('Юрий', 'Волновой', 'Юрьевич', dept_map['Физика'], 'Лектор', 'y.volnovoy@univ.ru', '+7-999-333-33-05', 'Магистр', '', '2017-09-01'),
        
        # Литература
        ('Татьяна', 'Поэтова', 'Александровна', dept_map['Литература'], 'Профессор', 't.poetova@univ.ru', '+7-999-444-44-01', 'Доктор наук', 'Профессор', '2001-09-01'),
        ('Борис', 'Прозаев', 'Борисович', dept_map['Литература'], 'Доцент', 'b.prozaev@univ.ru', '+7-999-444-44-02', 'Кандидат наук', 'Доцент', '2007-09-01'),
        ('Галина', 'Стихова', 'Ивановна', dept_map['Литература'], 'Старший преподаватель', 'g.stihova@univ.ru', '+7-999-444-44-03', 'Кандидат наук', '', '2010-09-01'),
        ('Лев', 'Романов', 'Львович', dept_map['Литература'], 'Ассистент', 'l.romanov@univ.ru', '+7-999-444-44-04', 'Магистр', '', '2021-09-01'),
        ('Вера', 'Сказкина', 'Владимировна', dept_map['Литература'], 'Лектор', 'v.skazkina@univ.ru', '+7-999-444-44-05', 'Магистр', '', '2018-09-01'),
    ]
    
    cursor.executemany(
        '''INSERT INTO teachers 
           (first_name, last_name, patronymic, department_id, position, email, phone, 
            academic_degree, academic_title, hire_date) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        teachers_data
    )
    
    conn.commit()
    conn.close()

# ==================== API ENDPOINTS ====================

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')

@app.route('/api/departments', methods=['GET'])
def get_departments():
    """Получить список всех кафедр"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM departments ORDER BY name')
        departments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(departments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers', methods=['GET'])
def get_teachers():
    """Получить список преподавателей с фильтрацией"""
    try:
        search = request.args.get('search', '').lower()
        dept_id = request.args.get('department', '')
        
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = '''
            SELECT t.id, t.first_name, t.last_name, t.patronymic, 
                   t.position, t.email, t.phone, t.academic_degree, 
                   t.academic_title, t.hire_date, d.name as department
            FROM teachers t
            JOIN departments d ON t.department_id = d.id
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += ' AND (LOWER(t.first_name) LIKE ? OR LOWER(t.last_name) LIKE ? OR LOWER(t.email) LIKE ?)'
            search_param = f'%{search}%'
            params.extend([search_param, search_param, search_param])
        
        if dept_id:
            query += ' AND t.department_id = ?'
            params.append(int(dept_id))
        
        query += ' ORDER BY t.last_name, t.first_name'
        
        cursor.execute(query, params)
        teachers = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(teachers)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers/<int:teacher_id>', methods=['GET'])
def get_teacher(teacher_id):
    """Получить информацию о конкретном преподавателе"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Информация о преподавателе
        cursor.execute('''
            SELECT t.*, d.name as department
            FROM teachers t
            JOIN departments d ON t.department_id = d.id
            WHERE t.id = ?
        ''', (teacher_id,))
        teacher = dict(cursor.fetchone() or {})
        
        if not teacher:
            return jsonify({'error': 'Преподаватель не найден'}), 404
        
        # Публикации
        cursor.execute('SELECT * FROM publications WHERE teacher_id = ?', (teacher_id,))
        teacher['publications'] = [dict(row) for row in cursor.fetchall()]
        
        # Повышение квалификации
        cursor.execute('SELECT * FROM professional_development WHERE teacher_id = ?', (teacher_id,))
        teacher['professional_development'] = [dict(row) for row in cursor.fetchall()]
        
        # Награды
        cursor.execute('SELECT * FROM awards WHERE teacher_id = ?', (teacher_id,))
        teacher['awards'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return jsonify(teacher)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers', methods=['POST'])
def create_teacher():
    """Добавить нового преподавателя"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO teachers 
            (first_name, last_name, patronymic, department_id, position, 
             email, phone, academic_degree, academic_title, hire_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('first_name'),
            data.get('last_name'),
            data.get('patronymic', ''),
            int(data.get('department_id')),
            data.get('position'),
            data.get('email', ''),
            data.get('phone', ''),
            data.get('academic_degree', ''),
            data.get('academic_title', ''),
            data.get('hire_date', datetime.now().strftime('%Y-%m-%d'))
        ))
        
        teacher_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({'id': teacher_id, 'message': 'Преподаватель добавлен'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers/<int:teacher_id>', methods=['PUT'])
def update_teacher(teacher_id):
    """Обновить информацию о преподавателе"""
    try:
        data = request.get_json()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE teachers
            SET first_name = ?, last_name = ?, patronymic = ?,
                department_id = ?, position = ?, email = ?, phone = ?,
                academic_degree = ?, academic_title = ?
            WHERE id = ?
        ''', (
            data.get('first_name'),
            data.get('last_name'),
            data.get('patronymic', ''),
            int(data.get('department_id')),
            data.get('position'),
            data.get('email', ''),
            data.get('phone', ''),
            data.get('academic_degree', ''),
            data.get('academic_title', ''),
            teacher_id
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Преподаватель обновлен'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers/<int:teacher_id>', methods=['DELETE'])
def delete_teacher(teacher_id):
    """Удалить преподавателя"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM teachers WHERE id = ?', (teacher_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'Преподаватель удален'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Получить статистику"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Всего преподавателей
        cursor.execute('SELECT COUNT(*) as total FROM teachers')
        total_teachers = cursor.fetchone()[0]
        
        # По кафедрам
        cursor.execute('''
            SELECT d.name, COUNT(t.id) as count
            FROM departments d
            LEFT JOIN teachers t ON d.id = t.department_id
            GROUP BY d.id, d.name
            ORDER BY d.name
        ''')
        by_department = [{'department': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        # По должностям
        cursor.execute('''
            SELECT position, COUNT(*) as count
            FROM teachers
            GROUP BY position
            ORDER BY count DESC
        ''')
        by_position = [{'position': row[0], 'count': row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'total_teachers': total_teachers,
            'by_department': by_department,
            'by_position': by_position
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ЗАПУСК ====================

if __name__ == '__main__':
    # Инициализируем БД
    init_db()
    load_initial_data()
    
    # Запускаем сервер
    print("=" * 60)
    print("Веб-приложение запущено!")
    print("Откройте в браузере: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
