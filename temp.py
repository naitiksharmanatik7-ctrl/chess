from PIL import Image

# Open the image
img = Image.open(r"assets/chess_peicess.svg.webp")

# Define new dimensions (width, height)
new_width, new_height = 360 , 120

# Resample using LANCZOS for high quality when downscaling
resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

# Save the scaled image
resized_img.save("chess_pieces.png")