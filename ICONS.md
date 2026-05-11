# Иконки приложения Смена WB

## Текущие иконки

- **favicon.svg** — иконка сайта (график/ПВЗ в фиолетовом стиле)
- **icon.ico** — иконка десктопной версии (создаётся скриптом)

## Создание icon.ico

Для генерации `icon.ico` и `favicon.png` выполните:

```bash
cd backend
python create_icon.py
```

Скрипт создаст файлы в папке `static/`.

## Своя иконка (WB / ПВЗ)

Чтобы заменить иконку на свою:

1. **Для сайта (favicon)** — положите файл `favicon.svg` или `favicon.png` в `backend/static/`
2. **Для десктопа** — положите `icon.ico` (32×32 или 48×48 пикселей) в `backend/static/`

### Форматы

- **Favicon:** SVG (рекомендуется) или PNG 32×32
- **Десктоп:** ICO (Windows) — можно конвертировать PNG в ICO через [convertio.co](https://convertio.co/png-ico/) или Pillow:

```python
from PIL import Image
img = Image.open('your_icon.png').resize((32, 32))
img.save('static/icon.ico', format='ICO')
```

### Идеи для иконки WB/ПВЗ

- Посылка / коробка (символ пункта выдачи)
- Календарь со стрелками (график смен)
- Комбинация: коробка + галочка
- Цвета Wildberries (фиолетовый/пурпурный)
