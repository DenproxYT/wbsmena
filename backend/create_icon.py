#!/usr/bin/env python3
"""Создаёт favicon.ico и icon.ico для приложения Смена WB (график/ПВЗ)."""
from PIL import Image, ImageDraw
import os

BASE = os.path.dirname(os.path.abspath(__file__))
STATIC = os.path.join(BASE, 'static')

def create_icon(size=64):
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Фон — скруглённый прямоугольник (градиент имитируем однотонным)
    padding = size // 8
    d.rounded_rectangle([padding, padding, size - padding, size - padding],
                       radius=size // 6, fill=(99, 102, 241))
    # Символ: столбики графика / смена
    w = max(2, size // 16)
    h1, h2, h3 = size * 0.4, size * 0.6, size * 0.3
    cx = size // 2
    d.rectangle([cx - w * 2 - 2, size - padding - int(h1), cx - 2, size - padding], fill='white')
    d.rectangle([cx - w, size - padding - int(h2), cx, size - padding], fill='white')
    d.rectangle([cx + 2, size - padding - int(h3), cx + w + 2, size - padding], fill='white')
    # Точка сверху
    r = size // 12
    d.ellipse([cx - r, padding, cx + r, padding + r * 2], fill='white')
    return img

def main():
    os.makedirs(STATIC, exist_ok=True)
    # PNG для favicon (32x32)
    img32 = create_icon(32)
    img32.save(os.path.join(STATIC, 'favicon.png'))
    # ICO для десктопа (32x32)
    img32.save(os.path.join(STATIC, 'icon.ico'), format='ICO')
    print('Создано: static/favicon.png, static/icon.ico')

if __name__ == '__main__':
    main()
