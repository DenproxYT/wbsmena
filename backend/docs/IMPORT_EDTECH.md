# Импорт обучения с edtech.rwb.ru

## Что нужно локально (секреты не отправляйте в чат)

В файле `.env` в папке `backend/`:

- `RWB_EDTECH_X_AUTH_KEY` — из DevTools → Network → любой запрос к `edtech.rwb.ru` → Request Headers → **X-Auth-Key**
- `RWB_EDTECH_COOKIE` — целиком строка **Cookie** из того же запроса (после входа в аккаунт)

Без актуальной сессии сервер отдаёт страницу «Добро пожаловать» / вход — парсеру нечего забирать.

## Запуск

```bash
pip install -r requirements.txt
python manage.py import_wb_pvz_materials --pvz-knowledge-block --limit 300
```

Страницы курсов имеют вид  
`/lms/ru/course?publicationid=...&unitid=...` — для каждого курса **нужны оба параметра**; в коде они больше не схлопываются в один URL.

## Если из HTML мало ссылок

1. Создайте текстовый файл, например `courses.txt`, по **одному полному URL в строке** (как в адресной строке браузера).
2. Запуск:

```bash
python manage.py import_wb_pvz_materials --pvz-knowledge-block --urls-file courses.txt --limit 400
```

## Что можно прислать разработчику **без** секретов

- **Только URL** XHR/Fetch из вкладки Network (без cookie), которые возвращают JSON со списком курсов или материалов.
- **Фрагмент JSON** ответа (замазать id/токены), чтобы понять структуру полей.
- Файл **`--dump-first-html page.html`** после успешной загрузки (без ваших cookie внутри файла обычно нет, но проверьте).

**Не присылайте:** полный Cookie, X-Auth-Key, `x-wbaas-token`, скриншоты с этими строками в открытом виде.

## PDF (основной текст обучения)

Импортер **скачивает PDF** по ссылкам из HTML и из JSON (в т.ч. ответы API), с теми же `Cookie` / `X-Auth-Key`, и заголовком **`Referer`** со страницы курса.

- Текст извлекается библиотекой **pypdf** (нужен текстовый слой в PDF).
- **Скан-копии** без текстового слоя в слайдах будет пометка «скан»; для OCR нужны другие инструменты.

```bash
pip install -r requirements.txt
python manage.py import_wb_pvz_materials --pvz-knowledge-block --urls-file courses.txt --limit 400
```

Отключить PDF: `--no-pdf`. Лимит файлов: `--max-pdfs 200`.

Если PDF не качается (ответ не `%PDF`), обновите **Cookie** в `.env` с той же сессии, где в браузере открывается файл.
