import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os.path as op
import os

metric='md'

# Define crop margins (top, bottom, left, right)
crop_top = 200
crop_bottom = 200
crop_left = 200
crop_right = 200

working_dir = os.getcwd()

tract_ids = ['ARC', 'ATR', 'IFO', 'ILF', 'SLF', 'UNC', 'CST']

for tid in tract_ids:

    image_files = [f'{metric}_F_{tid}_L.png', f'{metric}_F_{tid}_R.png', f'{metric}_M_{tid}_L.png', f'{metric}_M_{tid}_R.png']

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

    # Add text to the figure
    fig.text(0.5, 0.95, f"Female {metric.upper()} {tid}", fontsize=20, ha='center', va='center', color='black')
    fig.text(0.5, 0.45, f"Male {metric.upper()} {tid}", fontsize=20, ha='center', va='center', color='black')

    plt.tight_layout()
    plt.savefig(op.join(working_dir, f'figure_{metric}_{tid}.png'))
    plt.show()



