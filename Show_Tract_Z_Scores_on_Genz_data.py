import os
import os.path as op
import nibabel as nib
import numpy as np
import shutil
import pandas as pd
from fury import actor, window
from fury.colormap import create_colormap
from matplotlib import pyplot as plt
from dipy.io.stateful_tractogram import StatefulTractogram, Space
from Utility_Functions import load_z_p_data, lines_as_tubes, trim_to_central_60, check_orientation
from Utility_Functions import view_middle_slice, extract_fiber_dict
from nibabel.orientations import aff2axcodes

subj='genz323'
sex = 'M'
metric = "md"
check_orientation_flag = 0
working_dir = os.getcwd()
out_folder = working_dir
home_dir = os.path.expanduser("~")
img_dir = 'individual_modality_figs' # directory to place output images into
use_highres_for_glass_brain = 1

# Extract streamlines from .mat file for this subject
print("Extracting streamlines")
data_folder = f"{working_dir}/genz323/dti64trilin/"
fiber_dict = extract_fiber_dict(op.join(data_folder, 'fibers/MoriGroups_Cortex_clean_D5_L4.mat'))

for sex in ['F', 'M']:

    # Load tract statistics data
    z_score_filepath =f"{home_dir}/Documents/GenZ/Genz White Matter Myelin covid analysis/Z_score_by_node/one_hundred_splits/"
    if sex == "M":
        z_score_filename = f"{metric}_100split_node_stats_male.csv"
    else:
        z_score_filename = f"{metric}_100split_node_stats_female.csv"

    # Set image data paths
    # ----------------------------
    img_data_path = op.join(working_dir, f'{subj}/dti64trilin/bin')
    dt6_path = op.join(working_dir, f'{subj}/dti64trilin')

    # Read brain anatomy imaging data into memory
    # -------------------
    if use_highres_for_glass_brain:
        brain_mask_img = nib.load(op.join(img_data_path, f'sub-{subj}-visit2-MEMP-orig_magnet_space_bet.nii.gz'))
        brain_mask_img = nib.as_closest_canonical(brain_mask_img) # convert brain image to RAS orientation
        brain_mask_data = brain_mask_img.get_fdata()
        brain_mask_data = (brain_mask_data > 0).astype(np.uint8)
    else:
        brain_mask_img = nib.load(op.join(img_data_path, 'brainMask.nii.gz'))
        brain_mask_data = brain_mask_img.get_fdata()

    # Loop through tracts and show glass brain for each
    # ----------------------
    tract_ids = fiber_dict.keys()

    if metric == 'mpf':
        tract_ids.remove('Left Uncinate')
        tract_ids.remove('Right Uncinate')

    for tid in tract_ids:
        print(tid)

        # Load zscore values
        zvect, pvect = load_z_p_data(z_score_filepath, z_score_filename, tid.replace(' ', '_'))

        # Load tract streamlines
        sft = StatefulTractogram(fiber_dict[tid],
                                 reference=brain_mask_img,
                                 space=Space.RASMM)

        sft.to_vox()

        # Trim streamlines to the central 60%
        aligned_streamlines = trim_to_central_60(sft.streamlines)

        # Making a `scene`
        scene = window.Scene()
        scene.background((1, 1, 1))

        # Display glass brain
        brain_actor = actor.contour_from_roi(brain_mask_data, color=[0, 0, 0], opacity=0.05)
        scene.add(brain_actor)

        # Create an empty list for streamline actors
        streamline_actors = []

        for sl in aligned_streamlines:
            # interpolate the 60 tract profiles values to match the number of points
            # in the streamline:
            interpolated_z_values = np.interp(np.linspace(0, 1, sl.shape[0]),
                                            np.linspace(0, 1, len(zvect)),
                                            zvect)

            interpolated_p_values = np.interp(np.linspace(0, 1, len(sl)),
                                              np.linspace(0, 1, len(pvect)),
                                              pvect)

            # Apply a colormap to non significant values.

            if sex == 'M':
                # Make them blue
                colors = np.tile([0, 0, 1], (len(interpolated_z_values), 1))
            else:
                # Make them red
                colors = np.tile([1, 0, 0], (len(interpolated_z_values), 1))

            # Define a green
            my_green = ( 0/ 255, 255 / 255, 0 / 255)  # Normalized RGB values

            # Find indices where the interpolated p_values <0.05
            significant_mask = interpolated_p_values < 0.05

            # Override colors for significant values
            colors[significant_mask] = my_green

            if check_orientation_flag == 1:
                colors = check_orientation(interpolated_z_values)

            # Create streamline actor and add it to the list
            streamline_actor = actor.line([sl], colors=colors)
            streamline_actors.append(streamline_actor)

        # Add all streamline actors to the scene
        for sactor in streamline_actors:
            scene.add(sactor)

        scene.background((1, 1, 1))

        # if tid.startswith("L"):
        #     scene.set_camera(position=(-511.45, -62.25, 13.31),
        #                      focal_point=(2.00, -2.00, 8.00),
        #                      view_up=(0.02, -0.11, 0.99))
        #
        # elif "Callosum" in tid:
        #     scene.set_camera(position=(-457.39, -45.17, 241.22),
        #                      focal_point=(2.00, -2.00, 8.00),
        #                      view_up=(0.46, -0.14, 0.88))

        window.show(scene, size=(1200, 1200), reset_camera=False)
            #
            # scene.camera_info()

            # os.makedirs(op.join(out_folder, img_dir), exist_ok=True)

            # window.record(
            #     scene=scene,
            #     out_path=op.join(out_folder, img_dir, f'{metric}_{sex}_Left_{tid}.png'),
            #     size=(1200, 1200))
            #
            # scene.set_camera(position=(438.77, -86.28, 271.47),
            #                  focal_point=(2.00, -2.00, 8.00),
            #                  view_up=(-0.52, -0.02, 0.85))
            #
            # window.show(scene, size=(1200, 1200), reset_camera=False)
            #
            # scene.camera_info()

            # os.makedirs(op.join(out_folder, img_dir), exist_ok=True)

            # window.record(
            #     scene=scene,
            #     out_path=op.join(out_folder, img_dir, f'{metric}_{sex}_Right_{tid}.png'),
            #     size=(1200, 1200))

        # else:
            # scene.set_camera(position=(516.43, -16.32, -41.44),
            #                  focal_point=(2.00, -2.00, 8.00),
            #                  view_up=(0.09, -0.05, 0.99))

        # if "Callosum" not in tid:

            # window.show(scene, size=(1200, 1200), reset_camera=False)

            # scene.camera_info()

            # window.record(
            #     scene=scene,
            #     out_path=op.join(out_folder, img_dir, f'{metric}_{sex}_{tid}.png'),
            #     size=(1200, 1200))

