from PIL import Image, ImageDraw

# Create a square canvas
size = 256  # typical icon high-res
img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Draw a minimalist car silhouette
body_top = size * 0.45
body_bottom = size * 0.65
draw.rectangle(
    [(size*0.2, body_top), (size*0.8, body_bottom)],
    fill=(0, 0, 0, 255)
)

# Car roof
draw.polygon(
    [
        (size*0.35, body_top),
        (size*0.45, size*0.3),
        (size*0.55, size*0.3),
        (size*0.65, body_top)
    ],
    fill=(0, 0, 0, 255)
)

# Wheels
wheel_radius = int(size * 0.1)
for cx in [size*0.35, size*0.65]:
    draw.ellipse(
        [
            (cx - wheel_radius, body_bottom - wheel_radius/2),
            (cx + wheel_radius, body_bottom + wheel_radius)
        ],
        fill=(0, 0, 0, 255)
    )

# Save ICO
ico_path = r"C:/Users\Админ\Desktop\py\DataScince\Programs\Convertion\data/car_icon.ico"
img.save(ico_path, format="ICO")


