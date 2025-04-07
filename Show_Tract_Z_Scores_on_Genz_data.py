import os
import os.path as op
import nibabel as nib
import numpy as np
from nibabel.affines import apply_affine
import pandas as pd
from dipy.io.streamline import load_trk
from dipy.tracking.streamline import transform_streamlines
from fury import actor, window
from fury.colormap import create_colormap
from Utility_Functions import load_z_p_data, lines_as_tubes, trim_to_central_60, check_orientation

sex = 'M'
metric = "md"
check_orientation = 0
working_dir = os.getcwd()
home_dir = os.path.expanduser("~")

for sex in ['M', 'F']:

    # Load tract statistics data
    z_score_filepath =f"{home_dir}/Documents/GenZ/Genz White Matter Myelin covid analysis/Z_score_by_node/one_hundred_splits/"
    if sex == "M":
        z_score_filename = f"{metric}_100split_node_stats_male.csv"
    else:
        z_score_filename = f"{metric}_100split_node_stats_female.csv"

    out_folder = os.getcwd()

    # Get image data f
    # ----------------------------
    img_data_path = op.join(working_dir, 'genz323/dti64trilin/bin')
    bundle_path = op.join(working_dir, 'new_trk_files')
    dt6_path = op.join(working_dir, 'genz323/dti64trilin')

    # Read brain anatomy imaging data into memory
    # ----------------------
    fa_img = nib.load(op.join(img_data_path, 'mpfcoreg12.nii.gz'))
    fa = fa_img.get_fdata()
    brain_mask_img = nib.load(op.join(img_data_path, 'highres2padded_lowres_mask.nii.gz'))
    brain_mask_data = brain_mask_img.get_fdata()

    # Get affine data
    brain_affine = brain_mask_img.affine
    brain_shape = brain_mask_img.shape
    fa_affine = fa_img.affine
    inv_affine = np.linalg.inv(brain_affine)

    # Loop through tracts and show glass brain for each
    # ----------------------
    old_tract_ids = ['ARC_L', 'ARC_R', 'ATR_L', 'ATR_R', 'IFO_L', 'IFO_R', 'ILF_L', 'ILF_R', 'SLF_L', 'SLF_R', 'UNC_L', 'UNC_R', 'CST_L', 'CST_R']

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

        # Transform streamlines to brain mask space
        aligned_streamlines = [apply_affine(inv_affine, s) for s in streamlines]

        # Trim streamlines to the central 60%
        aligned_streamlines = trim_to_central_60(aligned_streamlines)

        streamline_points = np.vstack(aligned_streamlines)  # Flatten all points into one array

        # Making a `scene`
        scene = window.Scene()
        scene.background((1, 1, 1))

        print(type(actor))

        # Display glass brain
        brain_actor = actor.contour_from_roi(brain_mask_data, affine=brain_affine, color=[0, 0, 0], opacity=0.05)
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

            # Define a solid yellow color
            light_yellow = np.array([1, 1, 0.5])

            # Find indices where the interpolated p_values <0.05
            significant_mask = interpolated_p_values < 0.05

            # Override colors for significant values
            colors[significant_mask] = light_yellow

            if check_orientation == 1:
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
        else:
            scene.set_camera(position=(516.43, -16.32, -41.44),
                             focal_point=(2.00, -2.00, 8.00),
                             view_up=(0.09, -0.05, 0.99))

        window.show(scene, size=(1200, 1200), reset_camera=False)

        scene.camera_info()

        # window.record(
        #     scene=scene,
        #     out_path=op.join(out_folder, 'individual_modality_figs', f'{metric}_{sex}_{tid}.png'),
        #     size=(1200, 1200))




