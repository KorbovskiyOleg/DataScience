from PIL import Image, ImageDraw
from pathlib import Path

# открытие изображения
src = Path(r"C:\Users\Админ\Desktop\Other\ChatGPT Image 30 дек. 2025 г., 13_12_46.png")
img = Image.open(src)

# Save ICO
ico_path = Path(r"C:\Users\Админ\Desktop\py\DataScince\Programs\Convertion\data\car_icon.ico")

img.save(str(ico_path), sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)], format='ICO')






