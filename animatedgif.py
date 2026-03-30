from PIL import Image

# Put your filenames here in the exact order you want
image_files = [
    "C:\\work\\handyman\\outlet 1.jpg",
    "C:\\work\\handyman\\outlet 2.jpg",
    "C:\\work\\handyman\\outlet 3.jpg",   # fix name if needed
    "C:\\work\\handyman\\outlet 4.jpg"
]

frames = [Image.open(f).convert("RGB") for f in image_files]

# Durations in milliseconds
# 1 second = 1000 ms for first three, 3 seconds = 3000 ms for last
durations = [1000, 1000, 1000, 3000]

frames[0].save(
    "C:\\work\\handyman\\outlet_progress.gif",
    format="GIF",
    append_images=frames[1:],
    save_all=True,
    duration=durations,
    loop=0          # 0 = infinite looping
)

print("Created outlet_progress.gif")