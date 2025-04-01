import os
import os.path as op
import nibabel as nib
from nibabel.affines import apply_affine
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dipy.io.streamline import load_trk
# from dipy.tracking.streamline import transform_streamlines
from fury import actor, window
from fury.colormap import create_colormap
# import AFQ.data.fetch as afd
from Utility_Functions import load_data, lines_as_tubes, trim_to_central_60, check_orientation
import scipy
from scipy.ndimage import rotate
from dipy.tracking.streamline import Streamlines, transform_streamlines
from dipy.core import geometry


sex = 'M'
metric = "fa"
check_orientation = 0
working_dir = os.getcwd()

for sex in ['M', 'F']:

    # Load tract statistics data
    z_score_filepath = "/Users/neva/Documents/GenZ/Genz White Matter Myelin covid analysis/Z_score_by_node/one_hundred_splits/"
    if sex == "M":
        z_score_filename = f"{metric}_100split_node_stats_male.csv"
    else:
        z_score_filename = f"{metric}_100split_node_stats_female.csv"

    out_folder = os.getcwd()

    # Get image data from HBN POD2
    # ----------------------------
    #
    img_data_path = op.join(working_dir, 'genz323/dti64trilin/bin')
    bundle_path = op.join(working_dir, 'new_trk_files')
    dt6_path = op.join(working_dir, 'genz323/dti64trilin')
    # Read brain anatomy imaging data into memory
    # ----------------------
    fa_img = nib.load(op.join(img_data_path, 'mpfcoreg12.nii.gz'))
    fa = fa_img.get_fdata()
    t1w_img = nib.load(op.join(img_data_path, 'mpfcoreg12.nii.gz'))
    t1w = t1w_img.get_fdata()
    brain_mask_img = nib.load(op.join(img_data_path, 'brainMask.nii.gz'))
    brain_mask_data = brain_mask_img.get_fdata()


    tensors_img = nib.load(op.join(img_data_path, 'tensors.nii.gz'))
    tensor_affine = tensors_img.affine

    fa_affine = fa_img.affine

    a=np.allclose(fa_img.affine, t1w_img.affine)

     # Loop through tracts and show glass brain for each
    # ----------------------
    tract_ids = ['Left_Arcuate', 'Right_Arcuate', 'Left_Thalamic_Radiation', 'Right_Thalamic_Radiation', 'Left_IFOF',
                 'Right_IFOF', 'Left_ILF', 'Right_ILF', 'Left_SLF', 'Right_SLF', 'Left_Uncinate', 'Right_Uncinate',
                 'Left_Corticospinal', 'Right_Corticospinal']

    if metric == 'mpf':
        tract_ids.remove('Left_Uncinate')
        tract_ids.remove('Right_Uncinate')

    brain_affine = brain_mask_img.affine
    brain_shape = brain_mask_img.shape
    inv_affine = np.linalg.inv(brain_affine)  # Inverse affine

    brain_min = np.dot(brain_affine, [0, 0, 0, 1])[:3]  # Transform first voxel (0,0,0)
    brain_max = np.dot(brain_affine, [brain_shape[0], brain_shape[1], brain_shape[2], 1])[:3]  # Transform last voxel

    print("Brain Mask Coordinate Range (min - max):")
    print("X:", brain_min[0], "-", brain_max[0])
    print("Y:", brain_min[1], "-", brain_max[1])
    print("Z:", brain_min[2], "-", brain_max[2])

    for tid in tract_ids:
        print(tid)

        # Load zscore values
        # zvect, pvect = load_data(z_score_filepath, z_score_filename, 'ARC_L')

        trk_path = op.join(bundle_path, f'{tid}.trk')
        if not op.exists(trk_path):
            print(f"Error: File {trk_path} not found!")

        inverse_affine = np.linalg.inv(fa_affine)

        # Load tract streamlines
        sft = load_trk(op.join(bundle_path, f'{tid}.trk'), 'same', bbox_valid_check=False)

        streamlines = sft.streamlines

        # Transform streamlines to brain mask space
        aligned_streamlines = [apply_affine(inv_affine, s) for s in streamlines]

        streamline_points = np.vstack(aligned_streamlines)  # Flatten all points into one array

        min_coords = streamline_points.min(axis=0)
        max_coords = streamline_points.max(axis=0)

        print("Streamline Coordinate Range (min - max):")
        print("X:", min_coords[0], "-", max_coords[0])
        print("Y:", min_coords[1], "-", max_coords[1])
        print("Z:", min_coords[2], "-", max_coords[2])

        # Create FURY scene
        scene = window.Scene()
        scene.background((1, 1, 1))

        # Add brain mask as a volume (adjust opacity to see streamlines)
        brain_actor = actor.contour_from_roi(brain_mask_data, affine=brain_affine, color=(1, 1, 1), opacity=0.1)
        scene.add(brain_actor)

        # Add streamlines
        streamline_actor = actor.line(aligned_streamlines, colors=(1, 0, 0))  # Red for streamlines
        scene.add(streamline_actor)

        # Display)
        window.show(scene, size=(1200, 1200), reset_camera=False)

        mystop=1

    #     # Check the orientation of the FA image
    #     fa_orientation = nib.orientations.io_orientation(fa_img.affine)
    #
    #     # Load the streamline data
    #     sft = load_trk(op.join(bundle_path, f'{tid}.trk'), 'same', bbox_valid_check=False)
    #     streamline_orientation = nib.orientations.io_orientation(sft.affine)
    #
    #     print("FA Image Orientation:", fa_orientation)
    #     print("Streamline Orientation:", streamline_orientation)
    #
    #     # Apply the FA affine matrix to each streamline
    #     affine = fa_affine[:3, :3]  # Only consider the rotation part of the affine matrix
    #
    #     # Transform the streamlines using the FA affine matrix
    #     transformed_streamlines = []
    #     for streamline in sft.streamlines:
    #         transformed_streamlines.append(np.dot(streamline, affine.T) + fa_affine[:3, 3])
    #
    #     # Create a new Streamlines object with the transformed streamlines
    #     transformed_sft = Streamlines(transformed_streamlines)
    #
    #     #
    #     # # If orientations are different, reorient the streamlines to match the FA image
    #     # if not np.array_equal(fa_orientation, streamline_orientation):
    #     #     sft.reorient(fa_orientation)
    #     #
    #     # tract_t1w = transform_streamlines(sft.streamlines, np.linalg.inv(fa_affine))
    #
    #     tract_t1w = transformed_sft
    #
    #     # Convert streamlines to tubes
    #     tract_actor = lines_as_tubes(tract_t1w, 8)
    #
    #     # Making a `scene`
    #     scene = window.Scene()
    #     #
    #     # # Trim streamlines to the central 60%
    #     # # tract_trimmed = trim_to_central_60(tract_t1w)
    #     # tract_trimmed = tract_t1w
    #     #
    #     # Clear the scene
    #     scene.clear()
    #
    #     # Display glass brain
    #     brain_actor = actor.contour_from_roi(brain_mask_data, color=[0, 0, 0], opacity=0.05)
    #     scene.add(brain_actor)
    #
    #     # Step 1: Get the bounding box of the streamlines (min and max values in all 3 dimensions)
    #     streamline_min = np.min(np.concatenate([sline for sline in tract_t1w], axis=0), axis=0)
    #     streamline_max = np.max(np.concatenate([sline for sline in tract_t1w], axis=0), axis=0)
    #
    #     print("Streamline bounding box after scaling and translation:")
    #     print("Min:", streamline_min)
    #     print("Max:", streamline_max)
    #
    #     # Step 2: Get the center and size of the streamlines
    #     streamline_center = (streamline_min + streamline_max) / 2
    #     streamline_size = np.max(streamline_max - streamline_min)
    #
    #     # Step 3: Scale the streamlines to fit the window
    #     scaling_factor = 0.5  # Adjust this factor if needed
    #     scaled_streamlines = []
    #
    #     for streamline in tract_t1w:
    #         scaled_streamlines.append((streamline - streamline_center) / streamline_size * scaling_factor)
    #
    #     scaled_streamlines = Streamlines(scaled_streamlines)
    #
    #     # Step 4: (Optional) Translate the streamlines to center them around the brain focal point
    #     brain_center = np.array([41.00, 59.00, 34.00])  # Focal point from your camera settings
    #
    #     translated_streamlines = []
    #     for streamline in scaled_streamlines:
    #         translated_streamlines.append(streamline + (brain_center - streamline_center))
    #
    #     # Step 5: Create a new Streamlines object with the translated streamlines
    #     translated_streamlines = Streamlines(translated_streamlines)
    #
    #     # Step 6: Convert the streamlines to tubes
    #     tract_actor = lines_as_tubes(translated_streamlines, 8)
    #
    #     # Step 7: Add the tract actor (streamlines) to the scene
    #     scene.add(tract_actor)
    #     # for sl in tract_t1w:
    #     #     # interpolate the 60 tract profiles values to match the number of points
    #     #     # in the streamline:
    #     #     interpolated_z_values = np.interp(np.linspace(0, 1, len(sl)),
    #     #                                     np.linspace(0, 1, len(zvect)),
    #     #                                     zvect)
    #     #
    #     #     interpolated_p_values = np.interp(np.linspace(0, 1, len(sl)),
    #     #                                       np.linspace(0, 1, len(pvect)),
    #     #                                       pvect)
    #     #
    #     #     # Apply a colormap to non significant values.
    #     #
    #     #     if sex == 'M':
    #     #         # Make them blue
    #     #         colors = np.tile([0, 0, 1], (len(interpolated_z_values), 1))
    #     #     else:
    #     #         # Make them red
    #     #         colors = np.tile([1, 0, 0], (len(interpolated_z_values), 1))
    #     #
    #     #     # Define a solid yellow color
    #     #     light_yellow = np.array([1, 1, 0.5])
    #     #
    #     #     # Find indices where the interpolated p_values <0.05
    #     #     significant_mask = interpolated_p_values < 0.05
    #     #
    #     #     # Override colors for significant values
    #     #     colors[significant_mask] = light_yellow
    #     #
    #     #     if check_orientation == 1:
    #     #         colors = check_orientation(interpolated_z_values)
    #     #
    #
    #         # line_actor = lines_as_tubes([sl], 2, colors=colors)
    #         # scene.add(line_actor)
    #
    #     scene.background((1, 1, 1))
    #     #
    #     # if tid.endswith("_L"):
    #     scene.set_camera(position=(293, 100, -0.62),
    #                      focal_point=(41.00, 59.00, 34.00),
    #                      view_up=(0.14, -0.05, 0.99))
    #     # else:
    #     #     scene.set_camera(position=(-230.00, 159.39, 49.73),
    #     #                      focal_point=(96.00, 114.00, 96.00),
    #     #                      view_up=(0.05, 0.00, 1.00))
    #     #
    #     window.show(scene, size=(1200, 1200), reset_camera=False)
    #     #
    #     # scene.camera_info()
    #
    # # #
    # #
    # #     tract_t1w = new_sft.streamlines
    #     # Convert streamlines to tubes
    #     tract_actor = lines_as_tubes(tract_t1w, 8)
    # # #
    # #     # Making a `scene`
    # #     scene = window.Scene()
    # #
    # #     # Trim streamlines to the central 60%
    # #     tract_trimmed = trim_to_central_60(tract_t1w)
    # #
    # #     # Clear the scene
    # #     scene.clear()
    # #
    # #     # Display glass brain
    # #     brain_actor = actor.contour_from_roi(brain_mask_data, color=[0, 0, 0], opacity=0.05)
    # #     scene.add(brain_actor)
    # #
    # #     for sl in tract_trimmed:
    # #         # interpolate the 60 tract profiles values to match the number of points
    # #         # in the streamline:
    # #         interpolated_z_values = np.interp(np.linspace(0, 1, len(sl)),
    # #                                         np.linspace(0, 1, len(zvect)),
    # #                                         zvect)
    # #
    # #         interpolated_p_values = np.interp(np.linspace(0, 1, len(sl)),
    # #                                           np.linspace(0, 1, len(pvect)),
    # #                                           pvect)
    # #
    # #         # Apply a colormap to non significant values.
    # #
    # #         if sex == 'M':
    # #             # Make them blue
    # #             colors = np.tile([0, 0, 1], (len(interpolated_z_values), 1))
    # #         else:
    # #             # Make them red
    # #             colors = np.tile([1, 0, 0], (len(interpolated_z_values), 1))
    # #
    # #         # Define a solid yellow color
    # #         light_yellow = np.array([1, 1, 0.5])
    # #
    # #         # Find indices where the interpolated p_values <0.05
    # #         significant_mask = interpolated_p_values < 0.05
    # #
    # #         # Override colors for significant values
    # #         colors[significant_mask] = light_yellow
    # #
    # #         if check_orientation == 1:
    # #             colors = check_orientation(interpolated_z_values)
    # #
    # #         line_actor = lines_as_tubes([sl], 2, colors=colors)
    # #         scene.add(line_actor)
    # #
    # #     scene.background((1, 1, 1))
    # #
    # #     if tid.endswith("_L"):
    # #         scene.set_camera(position=(430.00, 126.78, 74.70),
    # #                          focal_point=(96.00, 114.00, 96.00),
    # #                          view_up=(0.05, 0.00, 1.00))
    # #     else:
    # #         scene.set_camera(position=(-230.00, 159.39, 49.73),
    # #                          focal_point=(96.00, 114.00, 96.00),
    # #                          view_up=(0.05, 0.00, 1.00))
    # #
    # #     window.show(scene, size=(1200, 1200), reset_camera=False)
    # #
    # #     scene.camera_info()
    # #
    # #     # window.record(
    # #     #     scene=scene,
    # #     #     out_path=op.join(out_folder, 'individual_modality_figs', f'{metric}_{sex}_{tid}.png'),
    # #     #     size=(1200, 1200))
    # #
