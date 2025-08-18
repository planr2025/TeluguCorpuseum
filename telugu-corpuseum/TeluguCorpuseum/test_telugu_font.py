from PIL import Image, ImageDraw, ImageFont

font_path = "fonts/NotoSansTelugu.ttf"
font = ImageFont.truetype(font_path, 50)

img = Image.new("RGB", (500, 200), "white")
draw = ImageDraw.Draw(img)
draw.text((10, 80), "తెలుగు పరీక్ష", font=font, fill="black")
img.show()
