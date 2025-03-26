import os
import os.path as op
import nibabel as nib
import numpy as np
import pandas as pd
from dipy.io.streamline import load_trk
from dipy.tracking.streamline import transform_streamlines
from fury import actor, window
from fury.colormap import create_colormap
import AFQ.data.fetch as afd

from Utility_Functions import load_data, lines_as_tubes, trim_to_central_60

sex = 'M'
metric = "fa"

for sex in ['M', 'F']:

    # Load tract statistics data
    z_score_filepath = "/Users/neva/Documents/GenZ/Genz White Matter Myelin covid analysis/Z_score_by_node/one_hundred_splits/"
    if sex == "M":
        z_score_filename = f"{metric}_100split_node_stats_male.csv"
    else:
        z_score_filename = f"{metric}_100_node_stats_female.csv"

    out_folder = os.getcwd()

    # Get image data from HBN POD2
    # ----------------------------
    # afd.fetch_hbn_preproc(["NDARAA948VFH"])
    study_path = afd.fetch_hbn_afq(["NDARAA948VFH"])[1]
    deriv_path = op.join(study_path, "derivatives")
    afq_path = op.join(deriv_path,'afq','sub-NDARAA948VFH','ses-HBNsiteRU')
    bundle_path = op.join(afq_path,'bundles')

    # Read brain anatomy imaging data into memory
    # ----------------------
    fa_img = nib.load(op.join(afq_path,
                              'sub-NDARAA948VFH_ses-HBNsiteRU_acq-64dir_space-T1w_desc-preproc_dwi_model-DKI_FA.nii.gz'))
    fa = fa_img.get_fdata()
    t1w_img = nib.load(op.join(deriv_path,
                               'qsiprep/sub-NDARAA948VFH/anat/sub-NDARAA948VFH_desc-preproc_T1w.nii.gz'))
    t1w = t1w_img.get_fdata()
    brain_mask_img = nib.load(op.join(deriv_path,
        'qsiprep/sub-NDARAA948VFH/anat/sub-NDARAA948VFH_desc-brain_mask.nii.gz'))
    brain_mask_data = brain_mask_img.get_fdata()

    # Loop through tracts and show glass brain for each
    # ----------------------
    tract_ids = ['ARC_L', 'ARC_R', 'ATR_L', 'ATR_R', 'IFO_L', 'IFO_R', 'ILF_L', 'ILF_R', 'SLF_L', 'SLF_R', 'UNC_L', 'UNC_R', 'CST_L', 'CST_R']
    for tid in tract_ids:

        # Load zscore values
        zvect, pvect = load_data(z_score_filepath, z_score_filename, tid)

        # Load tract streamlines
        sft = load_trk(op.join(bundle_path,
                f'sub-NDARAA948VFH_ses-HBNsiteRU_acq-64dir_space-T1w_desc-preproc_dwi_space-RASMM_model-CSD_desc-prob-afq-{tid}_tractography.trk'), fa_img)

        # Transform streamlines into the T1w reference frame
        sft.to_rasmm()
        tract_t1w = transform_streamlines(sft.streamlines, np.linalg.inv(t1w_img.affine))

        # Convert streamlines to tubes
        tract_actor = lines_as_tubes(tract_t1w, 8)

        # Making a `scene`
        scene = window.Scene()

        # Trim streamlines to the central 60%
        tract_trimmed = trim_to_central_60(tract_t1w)

        # Clear the scene
        scene.clear()

        # Display glass brain
        brain_actor = actor.contour_from_roi(brain_mask_data, color=[0, 0, 0], opacity=0.05)
        scene.add(brain_actor)

        for sl in tract_trimmed:
            # interpolate the 60 tract profiles values to match the number of points
            # in the streamline:
            interpolated_z_values = np.interp(np.linspace(0, 1, len(sl)),
                                            np.linspace(0, 1, len(zvect)),
                                            zvect)

            interpolated_p_values = np.interp(np.linspace(0, 1, len(sl)),
                                              np.linspace(0, 1, len(pvect)),
                                              pvect)

            # Apply a colormap to non significant values. Make them all blue
            colors = np.tile([0, 0, 1], (len(interpolated_z_values), 1))
            # colors = create_colormap(interpolated_z_values, name='Blues')

            # Define a solid yellow color
            light_yellow = np.array([1, 1, 0.5])

            # Find indices where the interpolated p_values <0.05
            significant_mask = interpolated_p_values < 0.05

            # Override colors for significant values
            colors[significant_mask] = light_yellow

            line_actor = lines_as_tubes([sl], 2, colors=colors)
            scene.add(line_actor)

        scene.background((1, 1, 1))

        if tid.endswith("_L"):
            scene.set_camera(position=(430.00, 126.78, 74.70),
                             focal_point=(96.00, 114.00, 96.00),
                             view_up=(0.05, 0.00, 1.00))
        else:
            scene.set_camera(position=(-230.00, 159.39, 49.73),
                             focal_point=(96.00, 114.00, 96.00),
                             view_up=(0.05, 0.00, 1.00))

        # window.show(scene, size=(1200, 1200), reset_camera=False)

        # scene.camera_info()

        window.record(
            scene=scene,
            out_path=op.join(out_folder, f'{metric}_{sex}_{tid}.png'),
            size=(1200, 1200))




