from PIL import Image

# --- Paths ---
SOURCE_PNG = "assets/logo.png"  # high-res source PNG
OUTPUT_ICO = "assets/logo.ico"  # output ICO

# --- Sizes Windows uses ---
sizes = [(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]

# Open PNG and save as multi-size ICO
img = Image.open(SOURCE_PNG)
img.save(OUTPUT_ICO, format="ICO", sizes=sizes)

print(f"Multi-size ICO created at {OUTPUT_ICO}!")
