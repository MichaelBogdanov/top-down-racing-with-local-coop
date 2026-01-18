import os
from PIL import Image

def load_and_crop_image(file_path, name):
    # Загружаем изображение с помощью Pillow
    img = Image.open(file_path)

    # Получаем границы изображения
    img = img.convert("RGBA")  # Конвертируем в RGBA, если это необходимо
    bbox = img.getbbox()  # Получаем границы (bounding box) содержимого изображения

    # Обрезаем изображение по границам
    cropped_img = img.crop(bbox)

    # Сохраняем обрезанное изображение во временный файл
    cropped_img.save(f"images/cropped_{name}.png")


for sprite in [file for file in os.listdir("images") if file.endswith(".png")]:
    load_and_crop_image("images/" + sprite, sprite[:-4])