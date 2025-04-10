import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.lines as mlines
import os.path as op
import os
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from Utility_Functions import make_legend, overlay_images
import numpy as np
from PIL import Image

metric='fa'

# Define crop margins (top, bottom, left, right)
crop_top = 250
crop_bottom = 200
crop_left = 200
crop_right = 200

working_dir = os.getcwd()
profdir = os.path.join(working_dir, 'tract_profiles_from_R')
streamline_dir = os.path.join(working_dir, 'individual_modality_figs')

tract_ids = ['Arcuate', 'Thalamic_Radiation', 'IFOF', 'ILF', 'SLF', 'Uncinate', 'Corticospinal',
             'Callosum_Forceps_Major', 'Callosum_Forceps_Minor']

profiles_regions = ['Arcuate', 'Thalamic Radiation', 'IFOF', 'ILF', 'SLF', 'Uncinate', 'Corticospinal',
                    'Callosum Forceps Major','Callosum Forceps Minor']

# Create a mapping from tract_ids to profile_regions
tract_to_profile = dict(zip(tract_ids, profiles_regions))

if metric == 'mpf':
    tract_ids.remove('Uncinate')
    del tract_to_profile['Uncinate']

make_legend(working_dir, 'Accelerated')
make_legend(working_dir, 'Slowed')

for tid in tract_ids:
    print(f'{tid}')
    p = tract_to_profile[tid]

    if "Callosum" in tid:
        image_files = [f'{streamline_dir}/{metric}_F_Left_{tid}.png', f'{streamline_dir}/{metric}_F_Right_{tid}.png',
                   f'{streamline_dir}/{metric}_M_Left_{tid}.png',
                   f'{streamline_dir}/{metric}_M_Right_{tid}.png', f'{profdir}/tracts_{metric}_splits_100{p}_new_format.png',
                   f'{profdir}/tracts_{metric}_splits_100{p}_new_format.png']
    else:
        image_files = [f'{streamline_dir}/{metric}_F_Left_{tid}.png', f'{streamline_dir}/{metric}_F_Right_{tid}.png',
                   f'{streamline_dir}/{metric}_M_Left_{tid}.png',
                   f'{streamline_dir}/{metric}_M_Right_{tid}.png', f'{profdir}/tracts_{metric}_splits_100Left {p}_new_format.png',
                   f'{profdir}/tracts_{metric}_splits_100Right {p}_new_format.png']

    # Create figure
    fig, axes = plt.subplots(3, 2, figsize=(6, 8.4))

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
    fig.suptitle(f'{tid} {metric.upper()} ', fontsize=18, y=0.98, color='black', fontweight='bold')
    fig.text(0.5, 0.90, f"Female", fontsize=18, ha='center', va='center', color='black')
    fig.text(0.5, 0.59, f"Male", fontsize=18, ha='center', va='center', color='black')
    fig.text(0.11, 0.86, "Left Hemisphere", fontsize=10, ha='center', va='center', color='black')
    fig.text(0.88, 0.86, "Right Hemisphere", fontsize=10, ha='center', va='center', color='black')
    fig.text(0.11, 0.573, "Left Hemisphere", fontsize=10, ha='center', va='center', color='black')
    fig.text(0.88, 0.573, "Right Hemisphere", fontsize=10, ha='center', va='center', color='black')

    plt.tight_layout(rect=[0, 0, 1, 0.90])  # lower the top margin to leave space for suptitle
    fig.subplots_adjust(top=0.85)  # indicates how close to the top the subplots are allowed to get
    fig.subplots_adjust(bottom=0.01)

    # plt.show()

    os.makedirs(op.join(working_dir, 'panel_figures'), exist_ok=True)
    plt.savefig(op.join(working_dir, 'panel_figures', f'figure_{metric}_{tid}.png'))

    # Load figure and add legend figure to it
    panel_img_path = op.join(working_dir ,'panel_figures', f'figure_{metric}_{tid}.png')

    if (metric == 'fa' and tid in ['IFOF', 'ILF']):
        legend_img_path = op.join(working_dir, 'custom_legend_Slowed.png')
    else:
        legend_img_path = op.join(working_dir, 'custom_legend_Accelerated.png')

    save_img_path = op.join(working_dir, 'panel_figures', f'combined_panel_figure_{metric}_{tid}.png')

    combined_img = overlay_images(panel_img_path, legend_img_path, save_img_path, position=(245, 550))

    combined_img.show()









