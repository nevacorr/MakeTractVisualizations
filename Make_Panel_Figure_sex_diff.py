import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.lines as mlines
import os.path as op
import os
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from Utility_Functions import make_legend, overlay_images, print_axis_size, resize_line_plot, resize_line_plot_callosum
from  matplotlib import gridspec
import numpy as np
from PIL import Image

metric='fa'

# Define crop margins (top, bottom, left, right)
crop_top = 250
crop_bottom = 200
crop_left = 200
crop_right = 200
crop_top_callosum = 210
crop_bottom_callosum = 180

working_dir = os.getcwd()
profdir = os.path.join(working_dir, 'tract_profiles_from_R')
streamline_dir = os.path.join(working_dir, 'individual_modality_figs')
os.makedirs(op.join(working_dir, 'panel_figures'), exist_ok=True)

tract_ids = ['Arcuate', 'Thalamic_Radiation', 'IFOF', 'ILF', 'SLF', 'Uncinate', 'Corticospinal',
             'Callosum_Forceps_Major', 'Callosum_Forceps_Minor']

profiles_regions = ['Arcuate', 'Thalamic Radiation', 'IFOF', 'ILF', 'SLF', 'Uncinate', 'Corticospinal',
                    'Callosum Forceps Major','Callosum Forceps Minor']

# Create a mapping from tract_ids to profile_regions
tract_to_profile = dict(zip(tract_ids, profiles_regions))

make_legend(working_dir, 'Accelerated')
make_legend(working_dir, 'Slowed')

for tid in tract_ids:
    print(f'{tid}')

    if any(sub in tid for sub in ["Arcuate", "Corticospinal", "IFOF", "Uncinate", "Thalamic_Radiation"]):

        p = tract_to_profile[tid]

        image_files = [f'{streamline_dir}/{metric}_F_Left_{tid}.png', f'{streamline_dir}/{metric}_F_Right_{tid}.png',
                   f'{streamline_dir}/{metric}_M_Left_{tid}.png',
                   f'{streamline_dir}/{metric}_M_Right_{tid}.png', f'{profdir}/tracts_{metric}_splits_100Left {p}_new_format_gam.png',
                   f'{profdir}/tracts_{metric}_splits_100Right {p}_new_format_gam.png']

        # Create figure
        fig, axes = plt.subplots(3, 2, figsize=(6, 8.4))

        # Flatten axes to a 1D list
        axes = axes.ravel()

        # Loop through images and plot them
        for i, (ax, img_path) in enumerate(zip(axes, image_files)):
            img = mpimg.imread(img_path)  # Read image

            # Crop only the first four (brain) images (don't crop line plots)
            if i < 4:
                h, w, _ = img.shape  # Get image dimensions
                img = img[crop_top:h - crop_bottom, crop_left:w - crop_right]

            # Crop title off of line plots
            if i >=4:
                img[:112, :, :] = 1  # Set top rows to 1 (white)

            ax.imshow(img)  # Display image
            ax.axis("off")

        # Add text to the figure
        fig.suptitle(f'{tid.replace("_", " ")} {metric.upper()} ', fontsize=18, y=0.98, color='black', fontweight='bold')
        fig.text(0.5, 0.9, f"Female", fontsize=18, ha='center', va='center', color='black')
        fig.text(0.5, 0.61, f"Male", fontsize=18, ha='center', va='center', color='black')
        fig.text(0.26, 0.93, "Left Hemisphere", fontsize=12, ha='center', va='center', color='black')
        fig.text(0.75, 0.93, "Right Hemisphere", fontsize=12, ha='center', va='center', color='black')

        plt.tight_layout(rect=[0, 0, 1, 0.90])  # lower the top margin to leave space for suptitle
        fig.subplots_adjust(top=0.90)  # indicates how close to the top the subplots are allowed to get
        fig.subplots_adjust(bottom=0.01)

        # Move the first and second image down slightly
        for i in [0, 1]:
            pos = axes[i].get_position()  # get current position [x0, y0, width, height]
            new_y0 = pos.y0 - 0.014  # move down
            axes[i].set_position([pos.x0, new_y0, pos.width, pos.height])

        print_axis_size(fig, axes)
        fig6_width, fig6_height = fig.get_size_inches()
        pos6 = axes[-1].get_position()  #position of bottom axis of 6 axis figure

        plt.savefig(op.join(working_dir, 'panel_figures', f'figure_{metric}_{tid}.png'), dpi=300)

        # Load figure and add legend figure to it
        panel_img_path = op.join(working_dir ,'panel_figures', f'figure_{metric}_{tid}.png')

        legend_img_path = op.join(working_dir, 'custom_legend_Accelerated.png')

        save_img_path = op.join(working_dir, 'panel_figures', f'combined_panel_figure_{metric}_{tid}.png')

        combined_img = overlay_images(panel_img_path, legend_img_path, save_img_path, position=(750, 1660))
        combined_img.show()


    if any(sub in tid for sub in ["Arcuate", "ILF", "SLF", "IFOF"]):

        p = tract_to_profile[tid]

        for hem in ['Left', 'Right']:

            image_files = [f'{streamline_dir}/{metric}_F_{hem}_{tid}.png',
                           f'{streamline_dir}/{metric}_M_{hem}_{tid}.png',
                           f'{profdir}/tracts_{metric}_splits_100{hem} {p}_new_format_gam.png'
            ]

            # Create figure
            fig, axes = plt.subplots(3, 1, figsize=(4, 8.4))

            # Flatten axes to a 1D list
            axes = axes.ravel()

            # Loop through images and plot them
            for i, (ax, img_path) in enumerate(zip(axes, image_files)):
                img = mpimg.imread(img_path)  # Read image

                # Crop only the first two (brain) images (don't crop line plots)
                if i < 2:
                    h, w, _ = img.shape  # Get image dimensions
                    img = img[crop_top:h - crop_bottom, crop_left:w - crop_right]

                # Crop title off of line plots
                if i >=2:
                    img[:110, :, :] = 1  # Set top rows to 1 (white)

                ax.imshow(img)  # Display image
                ax.axis("off")

            # Add text to the figure
            fig.suptitle(f'{tid.replace("_", " ")} {metric.upper()} ', fontsize=18, y=0.98, color='black', fontweight='bold')
            fig.text(0.5, 0.9, f"Female", fontsize=18, ha='center', va='center', color='black')
            fig.text(0.5, 0.61, f"Male", fontsize=18, ha='center', va='center', color='black')
            fig.text(0.5, 0.93, f'{hem} Hemisphere', fontsize=12, ha='center', va='center', color='black')

            plt.tight_layout(rect=[0, 0, 1, 0.90])  # lower the top margin to leave space for suptitle
            fig.subplots_adjust(top=0.90)  # indicates how close to the top the subplots are allowed to get
            fig.subplots_adjust(bottom=0.01)

            # Move the first image down slightly
            for i in [0]:
                pos = axes[i].get_position()  # get current position [x0, y0, width, height]
                new_y0 = pos.y0 - 0.014  # move down
                axes[i].set_position([pos.x0, new_y0, pos.width, pos.height])

            # Make the lineplot size and position match what it is in the 6 axis plot
            resize_line_plot(pos6, fig6_width, fig6_height, fig, axes)
            print_axis_size(fig, axes)

            # Cover up a little of the title visible in the line plot axis
            # Get the last axis and the image extent
            last_ax = axes[2]
            img = last_ax.images[0]  # the image you plotted with imshow

            # Get axis limits in display coordinates
            x0, x1 = last_ax.get_xlim()
            y0, y1 = last_ax.get_ylim()

            # Decide how much vertical fraction to cover (0-1)
            cover_frac = 0.09  # cover top 9% of the image

            # Draw a white rectangle over the top portion
            last_ax.add_patch(
                plt.Rectangle(
                    (x0, y1 - cover_frac * (y1 - y0)),  # bottom-left corner of rectangle
                    x1 - x0,  # width of rectangle
                    cover_frac * (y1 - y0),  # height of rectangle
                    color='white',
                    zorder=10  # make sure it's on top
                )
            )

            plt.savefig(op.join(working_dir, 'panel_figures', f'figure_{metric}_{tid}.png'), dpi=300)

            # Load figure and add legend figure to it
            panel_img_path = op.join(working_dir, 'panel_figures', f'figure_{metric}_{tid}.png')

            if (metric == 'fa' and tid in ['IFOF', 'ILF']):
                legend_img_path = op.join(working_dir, 'custom_legend_Slowed.png')
            else:
                legend_img_path = op.join(working_dir, 'custom_legend_Accelerated.png')

            save_img_path = op.join(working_dir, 'panel_figures', f'combined_panel_figure_{metric}_{tid}_{hem}.png')

            combined_img = overlay_images(panel_img_path, legend_img_path, save_img_path, position=(455, 1660))
            combined_img.show()

    if "Callosum" in tid:
        p = tract_to_profile[tid]

        image_files = [f'{streamline_dir}/{metric}_F_{tid}.png',
                       f'{streamline_dir}/{metric}_M_{tid}.png',
                       f'{profdir}/tracts_{metric}_splits_100{p}_new_format_gam.png',
                       f'{profdir}/tracts_{metric}_splits_100{p}_new_format_gam.png']

        # Create figure
        fig, axes = plt.subplots(3, 1, figsize=(4, 8.4))

        # Flatten axes to a 1D list
        axes = axes.ravel()

        # Loop through images and plot them
        for i, (ax, img_path) in enumerate(zip(axes, image_files)):
            img = mpimg.imread(img_path)  # Read image

            # Crop only the first two (brain) images (don't crop line plots)
            if i < 2:
                h, w, _ = img.shape  # Get image dimensions
                img = img[crop_top_callosum:h - crop_bottom_callosum, crop_left:w - crop_right]

            # Crop title off of line plots
            if i >=2:
                img[:110, :, :] = 1  # Set top 50 rows to 1 (white)

            ax.imshow(img)  # Display image
            ax.axis("off")

        # # Adjust the second axes position to move it down slightly
        pos1 = axes[1].get_position()  # get current position [x0, y0, width, height]
        new_y0 = pos1.y0 - 0.03  # move down by 0.05
        axes[1].set_position([pos1.x0, new_y0, pos1.width, pos1.height])

        # Add text to the figure
        fig.suptitle(f'{tid.replace("_", " ")} {metric.upper()} ', fontsize=18, y=0.98, color='black', fontweight='bold')
        fig.text(0.5, 0.92, f"Female", fontsize=18, ha='center', va='center', color='black')
        fig.text(0.5, 0.606, f"Male", fontsize=18, ha='center', va='center', color='black')
        fig.text(0.75, 0.90, "A", fontsize=14, ha='center', va='center', color='black')
        fig.text(0.75, 0.65, "P", fontsize=14, ha='center', va='center', color='black')
        fig.text(0.75, 0.585, "A", fontsize=14, ha='center', va='center', color='black')
        fig.text(0.75, 0.34, "P", fontsize=14, ha='center', va='center', color='black')

        plt.tight_layout(rect=[0, 0, 1, 0.90])  # lower the top margin to leave space for suptitle
        fig.subplots_adjust(top=0.90)  # indicates how close to the top the subplots are allowed to get
        fig.subplots_adjust(bottom=0.01)

        # Make the lineplot size and position match what it is in the 6 axis plot
        resize_line_plot_callosum(pos6, fig6_width, fig6_height, fig, axes)
        print_axis_size(fig, axes)

        plt.savefig(op.join(working_dir, 'panel_figures', f'figure_{metric}_{tid}.png'), dpi=300)

        # Load figure and add legend figure to it
        panel_img_path = op.join(working_dir, 'panel_figures', f'figure_{metric}_{tid}.png')

        save_img_path = op.join(working_dir, 'panel_figures', f'combined_panel_figure_{metric}_{tid}.png')
        legend_img_path = op.join(working_dir, 'custom_legend_Accelerated.png')

        combined_img = overlay_images(panel_img_path, legend_img_path, save_img_path, position=(455, 1680))
        combined_img.show()












