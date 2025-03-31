
import pandas as pd
import numpy as np
from fury import actor

def load_data(filepath, filename, tract):
    df = pd.read_csv(f"{filepath}{filename}")

    tract_mapping = {'Left.Arcuate': 'ARC_L', 'Right.Arcuate':'ARC_R', 'Left.Thalamic.Radiation':'ATR_L',
                       'Right.Thalamic.Radiation':'ATR_R', 'Left.IFOF':'IFO_L', 'Right.IFOF':'IFO_R', 'Left.ILF':'ILF_L',
                       'Right.ILF':'ILF_R', 'Left.SLF':'SLF_L', 'Right.SLF':'SLF_R', 'Left.Uncinate':'UNC_L',
                       'Right.Uncinate':'UNC_R', 'Left.Corticospinal':'CST_L', 'Right.Corticospinal':'CST_R'}

    df['Tract'] = df['Tract'].replace(tract_mapping)

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
        num_points = len(streamline)
        start_index = int(num_points * 0.2)  # 20% from the start
        end_index = int(num_points * 0.8)    # 20% from the end
        trimmed_streamline = streamline[start_index:end_index]
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