import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# List of image file paths
image_files = ['M_ARC_L.png', 'M_ARC_R.png', 'F_ARC_L.png', 'F_ARC_R.png']

# Create a figure and a set of subplots
fig, axes = plt.subplots(1, 4, figsize=(16, 4))

# Loop through images and plot them
for ax, img_path in zip(axes, image_files):
    img = mpimg.imread(img_path)  # Read image
    ax.imshow(img)  # Display image
    ax.axis("off")  # Hide axes

plt.tight_layout()
plt.show()