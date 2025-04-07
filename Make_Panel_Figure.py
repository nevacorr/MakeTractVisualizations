import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os.path as op
import os

metric='md'

# Define crop margins (top, bottom, left, right)
crop_top = 200
crop_bottom = 300
crop_left = 200
crop_right = 200

working_dir = os.getcwd()
profdir = os.path.join(working_dir, 'tract_profiles_from_R')
streamline_dir = os.path.join(working_dir, 'individual_modality_figs')

tract_ids = ['Arcuate', 'Thalamic_Radiation', 'IFOF', 'ILF', 'SLF', 'Uncinate', 'Corticospinal']
# tract_ids = ['ARC', 'ATR', 'IFO', 'ILF', 'SLF', 'UNC', 'CST']
profiles_regions = ['Arcuate', 'Thalamic.Radiation', 'IFOF', 'ILF', 'SLF', 'Uncinate', 'Corticospinal']

# Create a mapping from tract_ids to profile_regions
tract_to_profile = dict(zip(tract_ids, profiles_regions))

if metric == 'mpf':
    tract_ids.remove('Uncinate')
    del tract_to_profile['Uncinate']

for tid in tract_ids:
    print(f'{tid}')
    p = tract_to_profile[tid]
    image_files = [f'{streamline_dir}/{metric}_F_Left_{tid}.png', f'{streamline_dir}/{metric}_F_Right_{tid}.png',
                   f'{streamline_dir}/{metric}_M_Left_{tid}.png',
                   f'{streamline_dir}/{metric}_M_Right_{tid}.png', f'{profdir}/tracts_{metric}_splits_100Left.{p}.png',
                   f'{profdir}/tracts_{metric}_splits_100Right.{p}.png']

    # Create figure
    fig, axes = plt.subplots(3, 2, figsize=(6, 9))

    # Flatten axes to a 1D list
    axes = axes.ravel()

    # Loop through images and plot them
    for i, (ax, img_path) in enumerate(zip(axes, image_files)):
        img = mpimg.imread(img_path)  # Read image

        # Crop only the first four images
        if i < 4:
            h, w, _ = img.shape  # Get image dimensions
            img = img[crop_top:h - crop_bottom, crop_left:w - crop_right]

        ax.imshow(img)  # Display image
        ax.axis("off")

    # Add text to the figure
    fig.text(0.5, 0.98, f"Female {metric.upper()} {tid}", fontsize=18, ha='center', va='center', color='black')
    fig.text(0.5, 0.65, f"Male {metric.upper()} {tid}", fontsize=18, ha='center', va='center', color='black')
    fig.text(0.05, 0.98, "L", fontsize=15, ha='center', va='center', color='black')
    fig.text(0.95, 0.98, "R", fontsize=15, ha='center', va='center', color='black')
    fig.text(0.05, 0.65, "L", fontsize=15, ha='center', va='center', color='black')
    fig.text(0.95, 0.65, "R", fontsize=15, ha='center', va='center', color='black')

    plt.tight_layout()
    os.makedirs(op.join(working_dir, 'panel_figures'), exist_ok=True)
    plt.savefig(op.join(working_dir, 'panel_figures', f'figure_{metric}_{tid}.png'))
    plt.show()



