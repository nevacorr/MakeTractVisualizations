import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# List of image file paths
image_files = ['F_ARC_L.png', 'F_ARC_R.png', 'M_ARC_L.png', 'M_ARC_R.png']

# Define crop margins (top, bottom, left, right)
crop_top = 200
crop_bottom = 200
crop_left = 200
crop_right = 200

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(8, 8))

# Flatten axes to a 1D list
axes = axes.ravel()

# Loop through images and plot them
for ax, img_path in zip(axes, image_files):
    img = mpimg.imread(img_path)  # Read image
    h, w, _ = img.shape  # Get image dimensions
    img_cropped = img[crop_top:h-crop_bottom, crop_left:w-crop_right]  # Crop with fixed margins
    ax.imshow(img_cropped)  # Display cropped image
    ax.axis("off")  # Hide axes

plt.tight_layout()
plt.show()