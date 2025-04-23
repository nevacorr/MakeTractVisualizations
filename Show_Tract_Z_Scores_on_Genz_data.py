import os
import os.path as op
import nibabel as nib
import numpy as np
import shutil
from nibabel.affines import apply_affine
import pandas as pd
from dipy.io.streamline import load_trk
from dipy.tracking.streamline import transform_streamlines
from fury import actor, window
from fury.colormap import create_colormap
from matplotlib import pyplot as plt
from Utility_Functions import load_z_p_data, lines_as_tubes, trim_to_central_60, check_orientation
from Utility_Functions import view_middle_slice
from dipy.align.imaffine import (AffineRegistration, MutualInformationMetric, AffineMap)
from dipy.align.transforms import TranslationTransform3D, RigidTransform3D, AffineTransform3D
from Inspect_AFQ_mat_files import Inspect_AFQ_mat_files

subj='genz323'
sex = 'M'
metric = "fa"
check_orientation_flag = 0
working_dir = os.getcwd()
home_dir = os.path.expanduser("~")
img_dir = 'individual_modality_figs' # directory to place output images into
run_transform_lr_to_hr = 0

# Extract streamlines from .mat file for this subject
shutil.rmtree('new_trk_files', ignore_errors=True)
os.makedirs('new_trk_files')
print("Extracting streamlines")
Inspect_AFQ_mat_files(subj, working_dir)

for sex in ['F', 'M']:

    # Load tract statistics data
    z_score_filepath =f"{home_dir}/Documents/GenZ/Genz White Matter Myelin covid analysis/Z_score_by_node/one_hundred_splits/"
    if sex == "M":
        z_score_filename = f"{metric}_100split_node_stats_male.csv"
    else:
        z_score_filename = f"{metric}_100split_node_stats_female.csv"

    out_folder = os.getcwd()

    # Set image data paths
    # ----------------------------
    img_data_path = op.join(working_dir, f'{subj}/dti64trilin/bin')
    bundle_path = op.join(working_dir, 'new_trk_files')
    dt6_path = op.join(working_dir, f'{subj}/dti64trilin')

    # Read brain anatomy imaging data into memory
    # ----------------------
    lowres_img = nib.load(op.join(img_data_path, 'mpfcoreg12.nii.gz'))
    highres_img =  nib.load(op.join(img_data_path, f'sub-{subj}-visit2-MEMP-orig_magnet_space_bet.nii.gz'))
    lowres = lowres_img.get_fdata()
    highres = highres_img.get_fdata()

    view_middle_slice(lowres, 'lowres image')
    view_middle_slice(highres, 'highres image')

    brain_mask_img = highres_img
    # brain_mask_img = nib.load(op.join(img_data_path, 'high'))
    # brain_mask_img = nib.load(op.join(img_data_path, 'highres2lowres.nii.gz'))
    brain_mask_data = brain_mask_img.get_fdata()

    # Get image data and affines
    highres_affine = highres_img.affine
    lowres_affine = lowres_img.affine

    if run_transform_lr_to_hr == 1:

        # Registration
        reg = AffineRegistration(metric = MutualInformationMetric(nbins=32),
                                 level_iters=[1000, 100, 10],
                                 sigmas=[3.0, 1.0, 0.0],
                                 factors=[4, 2, 1])

        transform = AffineTransform3D()

        affine_map = reg.optimize(highres, lowres, transform, params0=None,
                                  static_grid2world=highres_affine,
                                  moving_grid2world=lowres_affine)

        # The final affine to transform points from low-res to high-res
        lowres_to_highres_affine = affine_map.affine

        # Resample low-res FA image into high-res space
        resampled_lowres_to_highres = affine_map.transform(lowres)

        # Save the resampled image in high-res space
        resampled_lowres_to_highres_img = nib.Nifti1Image(resampled_lowres_to_highres, highres_affine)

        nib.save(resampled_lowres_to_highres_img, 'lowresimg_in_highres_space.nii.gz')
        np.save('lowres_to_highres_affine.npy', lowres_to_highres_affine)

    else:

        # Load the previously saved affine and resampled image
        lowres_to_highres_affine = np.load('lowres_to_highres_affine.npy')
        resampled_lowres_to_highres_img = nib.load('lowresimg_in_highres_space.nii.gz')

    print('Highres affine matrix:')
    print(highres_affine)
    print('Lowres affine matrix:')
    print(lowres_affine)
    print("Low-res to High-res affine matrix:")
    print(lowres_to_highres_affine)
    # Get the origin (translation vector)
    lowres_to_highres_origin = lowres_to_highres_affine[:3, 3]
    highres_origin = highres_affine[:3, 3]

    print("Low-res to high res origin:", lowres_to_highres_origin)
    print("High-res origin:", highres_origin)
    lowres_orientation = lowres_to_highres_affine[:3, :3]
    highres_orientation = highres_affine[:3, :3]

    print("Low-res to high res orientation matrix:\n", lowres_orientation)
    print("High-res orientation matrix:\n", highres_orientation)

    # Low-res to high-res origin offset (difference between origins)
    origin_offset = highres_origin - lowres_to_highres_affine[:3, 3]

    # Update the affine matrix to account for the origin difference
    lowres_to_highres_affine[:3, 3] += origin_offset

    print("Low-res to high res origin after correction for origin offset:", lowres_to_highres_origin)
    print("High-res origin:", highres_origin)

    view_middle_slice(resampled_lowres_to_highres_img.get_fdata(), 'lowres to highres')

    inv_affine = np.linalg.inv(lowres_to_highres_affine)

    # Loop through tracts and show glass brain for each
    # ----------------------
    tract_ids = ['Left_Arcuate', 'Right_Arcuate', 'Left_Thalamic_Radiation', 'Right_Thalamic_Radiation', 'Left_IFOF',
                 'Right_IFOF', 'Left_ILF', 'Right_ILF', 'Left_SLF', 'Right_SLF', 'Left_Uncinate', 'Right_Uncinate',
                 'Left_Corticospinal', 'Right_Corticospinal', 'Callosum_Forceps_Major', 'Callosum_Forceps_Minor']

    if metric == 'mpf':
        tract_ids.remove('Left_Uncinate')
        tract_ids.remove('Right_Uncinate')

    for tid in tract_ids:
        print(tid)

        # Load zscore values
        zvect, pvect = load_z_p_data(z_score_filepath, z_score_filename, tid)

        # Load tract streamlines
        trk_path = op.join(bundle_path, f'{tid}.trk')
        sft = load_trk(op.join(bundle_path, f'{tid}.trk'), 'same', bbox_valid_check=False)
        streamlines = sft.streamlines

        # Transform streamlines to brain mask space]
        aligned_streamlines = transform_streamlines(streamlines, lowres_to_highres_affine)
        # aligned_streamlines = [apply_affine(lowres_to_highres_affine, s) for s in streamlines]

        # Trim streamlines to the central 60%
        aligned_streamlines = trim_to_central_60(aligned_streamlines)

        streamline_points = np.vstack(aligned_streamlines)  # Flatten all points into one array

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

        if tid.startswith("L"):
            scene.set_camera(position=(-511.45, -62.25, 13.31),
                             focal_point=(2.00, -2.00, 8.00),
                             view_up=(0.02, -0.11, 0.99))

        elif "Callosum" in tid:
            scene.set_camera(position=(-457.39, -45.17, 241.22),
                             focal_point=(2.00, -2.00, 8.00),
                             view_up=(0.46, -0.14, 0.88))

            window.show(scene, size=(1200, 1200), reset_camera=False)
            #
            # scene.camera_info()

            os.makedirs(op.join(out_folder, img_dir), exist_ok=True)

            window.record(
                scene=scene,
                out_path=op.join(out_folder, img_dir, f'{metric}_{sex}_Left_{tid}.png'),
                size=(1200, 1200))

            scene.set_camera(position=(438.77, -86.28, 271.47),
                             focal_point=(2.00, -2.00, 8.00),
                             view_up=(-0.52, -0.02, 0.85))

            window.show(scene, size=(1200, 1200), reset_camera=False)
            #
            # scene.camera_info()

            os.makedirs(op.join(out_folder, img_dir), exist_ok=True)

            window.record(
                scene=scene,
                out_path=op.join(out_folder, img_dir, f'{metric}_{sex}_Right_{tid}.png'),
                size=(1200, 1200))

        else:
            scene.set_camera(position=(516.43, -16.32, -41.44),
                             focal_point=(2.00, -2.00, 8.00),
                             view_up=(0.09, -0.05, 0.99))

        if "Callosum" not in tid:

            window.show(scene, size=(1200, 1200), reset_camera=False)

            # scene.camera_info()

            os.makedirs(op.join(out_folder, img_dir), exist_ok=True)

            window.record(
                scene=scene,
                out_path=op.join(out_folder, img_dir, f'{metric}_{sex}_{tid}.png'),
                size=(1200, 1200))

