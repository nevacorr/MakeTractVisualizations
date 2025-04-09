
import pandas as pd
import numpy as np
from fury import actor
import matplotlib.pyplot as plt
import matplotlib.lines as mlines


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

def make_legend():
    # Create a new figure
    fig, ax = plt.subplots(figsize=(1.2, 0.6))  # Adjust the size to fit your needs

    # Add lines (representing "Female", "Male", "Accelerated")
    line_female = mlines.Line2D([0, 0.2], [0.87, 0.87], color='red', lw=2, label='Female')
    line_male = mlines.Line2D([0, 0.2], [0.535, 0.535], color='blue', lw=2, label='Male')
    line_accel = mlines.Line2D([0, 0.2], [0.20, 0.20], color='green', lw=2, label='Accelerated')

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
    ax.text(0.3, 0.87, 'Female', color='black', fontsize=9, va='center')
    ax.text(0.3, 0.535, 'Male', color='black', fontsize=9, va='center')
    ax.text(0.3, 0.20, 'Accelerated', color='black', fontsize=9, va='center')

    # Show the figure
    plt.show()

    return fig, ax