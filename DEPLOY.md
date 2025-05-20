# Deployment Guide

## Server Information
- IP Address: 89.169.150.10
- Backend API: http://89.169.150.10:8000
- Frontend: http://89.169.150.10:3000

## Quick Start

1. Убедитесь, что на сервере установлены:
   - Docker
   - Docker Compose

2. Скопируйте все файлы проекта на сервер:
```bash
scp -r ./* user@89.169.150.10:/path/to/project/
```

3. Подключитесь к серверу:
```bash
ssh user@89.169.150.10
```

4. Перейдите в директорию проекта и запустите приложение:
```bash
cd /path/to/project
docker-compose up -d
```

5. Проверьте, что все сервисы запущены:
```bash
docker-compose ps
```

## Доступ к приложению

После успешного деплоя приложение будет доступно по следующим адресам:
- Frontend: http://89.169.150.10:3000
- Backend API: http://89.169.150.10:8000
- API Documentation: http://89.169.150.10:8000/docs

## Важные замечания

1. Перед запуском в production измените следующие значения в `docker-compose.yml`:
   - `POSTGRES_PASSWORD` - пароль для базы данных
   - `SECRET_KEY` - секретный ключ для JWT токенов
   - `REACT_APP_API_URL` - уже настроен на http://89.169.150.10:8000

2. Порты по умолчанию:
   - Backend API: 8000
   - Frontend: 3000
   - PostgreSQL: 5432 (внутренний порт)
   - Redis: 6379 (внутренний порт)

3. Данные сохраняются в Docker volumes:
   - `postgres_data` - данные PostgreSQL
   - `redis_data` - данные Redis

## Обновление приложения

Для обновления приложения:

1. Остановите контейнеры:
```bash
docker-compose down
```

2. Запустите снова:
```bash
docker-compose up -d --build
```

## Мониторинг

Проверка логов:
```bash
# Все сервисы
docker-compose logs

# Конкретный сервис
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
docker-compose logs redis
```

Проверка статуса:
```bash
docker-compose ps
```

## Безопасность

1. Убедитесь, что на сервере настроен файрвол и открыты только необходимые порты:
   - 3000 (Frontend)
   - 8000 (Backend API)

2. Рекомендуется настроить SSL/TLS для безопасного доступа по HTTPS

3. Регулярно меняйте пароли и секретные ключи

4. Настройте регулярное резервное копирование базы данных 