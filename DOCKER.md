# Запуск PVZ Automation через Docker

## Требования

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) установлен и запущен

## Команды

### Первый запуск (сборка и запуск)

```bash
cd c:\Users\Rengoku\Desktop\wb\pvz-automation
docker compose up --build
```

Сервер будет доступен по адресу: **http://localhost:8000/**

### Обычный запуск (без пересборки)

```bash
cd c:\Users\Rengoku\Desktop\wb\pvz-automation
docker compose up
```

### Запуск в фоне

```bash
docker compose up -d
```

### Переезд БД с SQLite на MySQL (один раз)

1) Снять дамп из текущей SQLite:
```bash
docker compose run --rm -e DB_ENGINE=sqlite web python manage.py dumpdata \
  --exclude auth.permission --exclude contenttypes \
  --natural-foreign --natural-primary \
  --output /app/sqlite_dump.json
```

2) Поднять MySQL и приложение:
```bash
docker compose up -d --build
```

3) Загрузить дамп в MySQL:
```bash
docker compose exec web python manage.py loaddata /app/sqlite_dump.json
```

4) Проверить:
```bash
docker compose exec web python manage.py check
```

### Остановка

```bash
docker compose down
```

### Просмотр логов

```bash
docker compose logs -f web
```

### Создание суперпользователя (админ)

```bash
docker compose exec web python manage.py createsuperuser
```

---

**Примечание:** Файл базы данных `db.sqlite3` сохраняется в папке `backend/` и не теряется при остановке контейнера.
