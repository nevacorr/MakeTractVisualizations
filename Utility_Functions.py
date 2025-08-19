
import pandas as pd
import numpy as np
from fury import actor
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import os.path as op
from PIL import Image
import h5py

def load_z_p_data(filepath, filename, tract):
    df = pd.read_csv(f"{filepath}{filename}")

    df['Tract'] = df['Tract'].str.replace('.', '_', regex=False)

    z = df.loc[df["Tract"] == tract, "Z_mean"].values
    adjp = df.loc[df["Tract"] == tract, "adjusted_p_value"].values
    return z, adjp

def lines_as_tubes(sl, line_width, **kwargs):
    line_actor = actor.line(sl, **kwargs)
    line_actor.GetProperty().SetRenderLinesAsTubes(1)
    line_actor.GetProperty().SetLineWidth(line_width)
    return line_actor

def trim_to_central_60(streamlines):
    trimmed_streamlines = []
    for streamline in streamlines:
        # Calculate the number of points to keep (60% of the streamline)
        num_points = streamline.shape[0]
        start_index = int(num_points * 0.2)  # 20% from the start
        end_index = int(num_points * 0.8)    # 20% from the end
        trimmed_streamline = streamline[start_index:end_index, :]
        trimmed_streamlines.append(trimmed_streamline)
    return trimmed_streamlines


def check_orientation(interpolated_z_values):
    def position_to_color(index, num_values):
        """Map position to a blue-white-red RGB color."""
        if index < num_values // 3:
            return [0, 0, 1]  # Blue for the first third
        elif index < 2 * num_values // 3:
            return [1, 1, 1]  # White for the middle third
        else:
            return [1, 0, 0]  # Red for the last third

    # Get the number of elements in interpolated_z_values
    num_values = len(interpolated_z_values)

    # Generate colors based on position
    colors = np.array([position_to_color(i, num_values) for i in range(num_values)])

    return colors

def make_legend(working_dir, label):
    # Create a new figure
    fig, ax = plt.subplots(figsize=(1.3, 0.7))

    my_purple = (0.89, 0.0, 0.89)
    my_green = (0.1, 0.7, 0.26)  # Normalized RGB values
    my_blue = (0.0, 0.0, 1.0)

    # Add lines (representing "Female", "Male", "Accelerated")
    line_female = mlines.Line2D([0, 0.2], [0.87, 0.87], color=my_green, lw=2, label='Female')
    line_male = mlines.Line2D([0, 0.2], [0.535, 0.535], color=my_purple, lw=2, label='Male')

    line_accel = mlines.Line2D([0, 0.2], [0.20, 0.20], color=my_blue, lw=2, label=label)

    # Add lines to the axis
    ax.add_line(line_female)
    ax.add_line(line_male)
    ax.add_line(line_accel)

    # Set the limits to ensure all lines fit within the figure
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Hide the axis
    ax.axis('off')

    # Add custom text labels for each line (to mimic a legend)
    ax.text(0.3, 0.87, 'Female', color='black', fontsize=10, va='center')
    ax.text(0.3, 0.535, 'Male', color='black', fontsize=10, va='center')
    ax.text(0.3, 0.20, label, color='black', fontsize=10, va='center')

    plt.savefig(op.join(working_dir, f'custom_legend_{label}.png'), dpi=300)

    # Show the figure
    # plt.show()

def overlay_images(big_image_path, small_image_path, save_path, position=(0, 0)):
    """
    Overlays a smaller image on a larger image at the specified position and saves the result.

    Parameters:
    - big_image_path: Path to the large image (background image).
    - small_image_path: Path to the small image (overlay image).
    - save_path: Path where the combined image will be saved.
    - position: Tuple (x, y) specifying the top-left position of the small image on the big image.
    """
    # Load the big image and small image
    big_img = Image.open(big_image_path)
    small_img = Image.open(small_image_path)

    # Ensure both images are in RGBA mode to handle transparency properly
    big_img_rgba = big_img.convert("RGBA")
    small_img_rgba = small_img.convert("RGBA")

    # Create a copy of the big image to overlay the small image on
    combined_img = big_img_rgba.copy()

    # Position of the small image
    x_offset, y_offset = position

    # Paste the small image onto the big image at the specified position
    combined_img.paste(small_img_rgba, (x_offset, y_offset), small_img_rgba)

    # Save the result to the specified path
    combined_img.save(save_path, dpi=(300, 300))

    print(f"Image saved to {save_path}")

    return combined_img

def view_middle_slice(image1, title, cmap='gray'):

    slice_index = image1.shape[2] // 2  # middle slice

    plt.figure(figsize=(6, 6))
    plt.imshow(image1[:, :, slice_index].T, cmap=cmap, origin='lower')
    plt.axis('off')
    plt.title(title)
    plt.tight_layout()
    plt.show(block=False)

def extract_fiber_dict(mat_file):
    data = h5py.File(mat_file)
    fg = data['fg']
    fibers = fg["fibers"]
    coords = [[np.array(data[data[fibers[jj][0]][0][ii]])
               for ii in range(data[fibers[jj][0]].shape[-1])]
             for jj in range(20)]
    name = fg["name"]
    names = [''.join([chr(ii) for ii in np.squeeze(np.array(data[name[jj][0]][:]))])
             for jj in range(20)]
    return dict(zip(names, coords))