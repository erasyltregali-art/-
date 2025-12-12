// ==================== ПЕРЕМЕННЫЕ ==================== 

let currentTeacherId = null;
let allTeachers = [];
let allDepartments = [];

// ==================== ИНИЦИАЛИЗАЦИЯ ==================== 

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

async function initializeApp() {
    // Загружаем кафедры
    await loadDepartments();
    
    // Загружаем преподавателей
    await loadTeachers();
    
    // Загружаем статистику
    await loadStatistics();
    
    // Привязываем обработчики событий
    attachEventListeners();
}

// ==================== ЗАГРУЗКА ДАННЫХ ==================== 

async function loadDepartments() {
    try {
        const response = await fetch('/api/departments');
        allDepartments = await response.json();
        
        // Заполняем select в форме
        const deptSelect = document.getElementById('department_id');
        const deptFilter = document.getElementById('department-filter');
        
        deptSelect.innerHTML = '<option value="">Выберите кафедру</option>';
        deptFilter.innerHTML = '<option value="">Все кафедры</option>';
        
        allDepartments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.id;
            option.textContent = dept.name;
            deptSelect.appendChild(option.cloneNode(true));
            deptFilter.appendChild(option);
        });
    } catch (error) {
        console.error('Ошибка загрузки кафедр:', error);
        showNotification('Ошибка при загрузке кафедр', 'error');
    }
}

async function loadTeachers() {
    try {
        const search = document.getElementById('search-input').value;
        const department = document.getElementById('department-filter').value;
        
        let url = '/api/teachers';
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (department) params.append('department', department);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        allTeachers = await response.json();
        
        renderTeachersTable();
        updateTeachersCount();
    } catch (error) {
        console.error('Ошибка загрузки преподавателей:', error);
        showNotification('Ошибка при загрузке преподавателей', 'error');
    }
}

async function loadStatistics() {
    try {
        const response = await fetch('/api/statistics');
        const stats = await response.json();
        
        // Общее количество
        document.getElementById('stat-total').textContent = stats.total_teachers;
        
        // По кафедрам
        const deptTable = document.getElementById('stats-by-dept');
        deptTable.innerHTML = '';
        const maxDept = Math.max(...stats.by_department.map(d => d.count), 1);
        
        stats.by_department.forEach(item => {
            const row = document.createElement('tr');
            const percentage = (item.count / maxDept) * 100;
            row.innerHTML = `
                <td>${item.department}</td>
                <td><strong>${item.count}</strong></td>
                <td>
                    <div class="bar-chart" style="width: ${percentage}%"></div>
                </td>
            `;
            deptTable.appendChild(row);
        });
        
        // По должностям
        const posTable = document.getElementById('stats-by-position');
        posTable.innerHTML = '';
        const maxPos = Math.max(...stats.by_position.map(p => p.count), 1);
        
        stats.by_position.forEach(item => {
            const row = document.createElement('tr');
            const percentage = (item.count / maxPos) * 100;
            row.innerHTML = `
                <td>${item.position}</td>
                <td><strong>${item.count}</strong></td>
                <td>
                    <div class="bar-chart" style="width: ${percentage}%"></div>
                </td>
            `;
            posTable.appendChild(row);
        });
    } catch (error) {
        console.error('Ошибка загрузки статистики:', error);
    }
}

// ==================== РЕНДЕРИНГ ==================== 

function renderTeachersTable() {
    const tbody = document.getElementById('teachers-tbody');
    
    if (allTeachers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Преподаватели не найдены</td></tr>';
        return;
    }
    
    tbody.innerHTML = allTeachers.map(teacher => `
        <tr>
            <td>
                <strong>${teacher.last_name} ${teacher.first_name} ${teacher.patronymic || ''}</strong>
            </td>
            <td>${teacher.position}</td>
            <td>${teacher.department}</td>
            <td>${teacher.email || '—'}</td>
            <td>${teacher.phone || '—'}</td>
            <td>${teacher.academic_degree || '—'}</td>
            <td>
                <div class="action-buttons">
                    <button class="btn btn-small btn-primary" onclick="viewTeacher(${teacher.id})">Просмотр</button>
                    <button class="btn btn-small btn-secondary" onclick="editTeacher(${teacher.id})">Редактировать</button>
                    <button class="btn btn-small btn-danger" onclick="deleteTeacher(${teacher.id})">Удалить</button>
                </div>
            </td>
        </tr>
    `).join('');
}

function updateTeachersCount() {
    const count = allTeachers.length;
    document.getElementById('teachers-count').textContent = `Всего преподавателей: ${count}`;
}

// ==================== МОДАЛЬНЫЕ ОКНА ==================== 

function openTeacherModal(title = 'Добавить преподавателя') {
    document.getElementById('modal-title').textContent = title;
    document.getElementById('teacher-form').reset();
    currentTeacherId = null;
    document.getElementById('teacher-modal').classList.add('active');
}

function closeTeacherModal() {
    document.getElementById('teacher-modal').classList.remove('active');
    document.getElementById('teacher-form').reset();
    currentTeacherId = null;
}

function openDetailModal(teacher) {
    const modal = document.getElementById('detail-modal');
    const content = document.getElementById('detail-content');
    
    const fio = `${teacher.last_name} ${teacher.first_name} ${teacher.patronymic || ''}`;
    document.getElementById('detail-title').textContent = fio;
    
    let html = `
        <div class="detail-content">
            <div class="detail-group">
                <div class="detail-label">Должность</div>
                <div class="detail-value">${teacher.position}</div>
            </div>
            <div class="detail-group">
                <div class="detail-label">Кафедра</div>
                <div class="detail-value">${teacher.department}</div>
            </div>
            <div class="detail-group">
                <div class="detail-label">Email</div>
                <div class="detail-value">${teacher.email || '—'}</div>
            </div>
            <div class="detail-group">
                <div class="detail-label">Телефон</div>
                <div class="detail-value">${teacher.phone || '—'}</div>
            </div>
            <div class="detail-group">
                <div class="detail-label">Ученая степень</div>
                <div class="detail-value">${teacher.academic_degree || '—'}</div>
            </div>
            <div class="detail-group">
                <div class="detail-label">Ученое звание</div>
                <div class="detail-value">${teacher.academic_title || '—'}</div>
            </div>
            <div class="detail-group">
                <div class="detail-label">Дата приема</div>
                <div class="detail-value">${teacher.hire_date || '—'}</div>
            </div>
    `;
    
    if (teacher.publications && teacher.publications.length > 0) {
        html += `
            <div class="detail-section">
                <h3>📄 Публикации</h3>
                <ul class="detail-list">
                    ${teacher.publications.map(p => `
                        <li>
                            <strong>${p.title}</strong><br>
                            <small>${p.journal || ''} (${p.publication_date || ''})</small>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    if (teacher.professional_development && teacher.professional_development.length > 0) {
        html += `
            <div class="detail-section">
                <h3>🎓 Повышение квалификации</h3>
                <ul class="detail-list">
                    ${teacher.professional_development.map(pd => `
                        <li>
                            <strong>${pd.course_name}</strong><br>
                            <small>${pd.completion_date || ''}</small>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    if (teacher.awards && teacher.awards.length > 0) {
        html += `
            <div class="detail-section">
                <h3>🏆 Награды</h3>
                <ul class="detail-list">
                    ${teacher.awards.map(a => `
                        <li>
                            <strong>${a.award_name}</strong><br>
                            <small>${a.award_date || ''}</small>
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;
    }
    
    html += '</div>';
    content.innerHTML = html;
    
    // Привязываем обработчики кнопок
    document.getElementById('edit-from-detail-btn').onclick = () => {
        closeDetailModal();
        editTeacher(teacher.id);
    };
    
    document.getElementById('delete-from-detail-btn').onclick = () => {
        closeDetailModal();
        deleteTeacher(teacher.id);
    };
    
    document.getElementById('close-detail-btn').onclick = closeDetailModal;
    
    currentTeacherId = teacher.id;
    modal.classList.add('active');
}

function closeDetailModal() {
    document.getElementById('detail-modal').classList.remove('active');
}

// ==================== ОПЕРАЦИИ С ПРЕПОДАВАТЕЛЯМИ ==================== 

async function viewTeacher(teacherId) {
    try {
        const response = await fetch(`/api/teachers/${teacherId}`);
        const teacher = await response.json();
        openDetailModal(teacher);
    } catch (error) {
        console.error('Ошибка загрузки деталей:', error);
        showNotification('Ошибка при загрузке информации', 'error');
    }
}

async function editTeacher(teacherId) {
    try {
        const response = await fetch(`/api/teachers/${teacherId}`);
        const teacher = await response.json();
        
        // Заполняем форму
        document.getElementById('first_name').value = teacher.first_name;
        document.getElementById('last_name').value = teacher.last_name;
        document.getElementById('patronymic').value = teacher.patronymic || '';
        document.getElementById('department_id').value = teacher.department_id;
        document.getElementById('position').value = teacher.position;
        document.getElementById('academic_degree').value = teacher.academic_degree || '';
        document.getElementById('academic_title').value = teacher.academic_title || '';
        document.getElementById('email').value = teacher.email || '';
        document.getElementById('phone').value = teacher.phone || '';
        document.getElementById('hire_date').value = teacher.hire_date || '';
        
        currentTeacherId = teacherId;
        openTeacherModal('Редактировать преподавателя');
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        showNotification('Ошибка при загрузке данных', 'error');
    }
}

async function deleteTeacher(teacherId) {
    if (!confirm('Вы уверены, что хотите удалить этого преподавателя?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/teachers/${teacherId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification('Преподаватель удален', 'success');
            await loadTeachers();
            await loadStatistics();
        } else {
            showNotification('Ошибка при удалении', 'error');
        }
    } catch (error) {
        console.error('Ошибка удаления:', error);
        showNotification('Ошибка при удалении', 'error');
    }
}

// ==================== ОБРАБОТКА ФОРМ ==================== 

async function handleTeacherFormSubmit(e) {
    e.preventDefault();
    
    const formData = {
        first_name: document.getElementById('first_name').value,
        last_name: document.getElementById('last_name').value,
        patronymic: document.getElementById('patronymic').value,
        department_id: document.getElementById('department_id').value,
        position: document.getElementById('position').value,
        academic_degree: document.getElementById('academic_degree').value,
        academic_title: document.getElementById('academic_title').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        hire_date: document.getElementById('hire_date').value
    };
    
    try {
        let response;
        
        if (currentTeacherId) {
            // Редактирование
            response = await fetch(`/api/teachers/${currentTeacherId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                showNotification('Преподаватель обновлен', 'success');
            }
        } else {
            // Добавление
            response = await fetch('/api/teachers', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });
            
            if (response.ok) {
                showNotification('Преподаватель добавлен', 'success');
            }
        }
        
        if (response.ok) {
            closeTeacherModal();
            await loadTeachers();
            await loadStatistics();
        } else {
            showNotification('Ошибка при сохранении', 'error');
        }
    } catch (error) {
        console.error('Ошибка сохранения:', error);
        showNotification('Ошибка при сохранении', 'error');
    }
}

// ==================== НАВИГАЦИЯ ==================== 

function switchView(viewName) {
    // Скрываем все виды
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    
    // Показываем нужный вид
    document.getElementById(`${viewName}-view`).classList.add('active');
    
    // Обновляем активную кнопку навигации
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Загружаем данные если нужно
    if (viewName === 'statistics') {
        loadStatistics();
    }
}

// ==================== УВЕДОМЛЕНИЯ ==================== 

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// ==================== ПРИВЯЗКА СОБЫТИЙ ==================== 

function attachEventListeners() {
    // Навигация
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            switchView(e.target.dataset.view);
        });
    });
    
    // Кнопка добавления преподавателя
    document.getElementById('add-teacher-btn').addEventListener('click', () => {
        openTeacherModal('Добавить преподавателя');
    });
    
    // Форма преподавателя
    document.getElementById('teacher-form').addEventListener('submit', handleTeacherFormSubmit);
    
    // Закрытие модального окна
    document.getElementById('cancel-btn').addEventListener('click', closeTeacherModal);
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', (e) => {
            if (e.target.closest('#teacher-modal')) {
                closeTeacherModal();
            } else if (e.target.closest('#detail-modal')) {
                closeDetailModal();
            }
        });
    });
    
    // Закрытие модального окна при клике вне содержимого
    document.getElementById('teacher-modal').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            closeTeacherModal();
        }
    });
    
    document.getElementById('detail-modal').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            closeDetailModal();
        }
    });
    
    // Фильтры и поиск
    document.getElementById('search-input').addEventListener('input', () => {
        loadTeachers();
    });
    
    document.getElementById('department-filter').addEventListener('change', () => {
        loadTeachers();
    });
    
    document.getElementById('reset-filters-btn').addEventListener('click', () => {
        document.getElementById('search-input').value = '';
        document.getElementById('department-filter').value = '';
        loadTeachers();
    });
}
