import os

import h5py
import numpy as np
import os.path as op
import os
from dipy.io.stateful_tractogram import StatefulTractogram, Space
from fury import actor, window
import nibabel as nib
from Utility_Functions import lines_as_tubes

working_dir = os.getcwd()

data_folder = f"{working_dir}/genz323/dti64trilin/"

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

fiber_dict = extract_fiber_dict(op.join(data_folder, 'fibers/MoriGroups_Cortex_clean_D5_L4.mat'))

# fiber_dict.keys()

tid = "Left Arcuate"

brain_mask = nib.load(op.join(data_folder, "bin", "brainMask.nii.gz"))
# brain_mask = nib.load(op.join(data_folder, "bin", "sub-genz323-visit2-MEMP-orig_Magnet_space_bet.nii.gz"))

sft = StatefulTractogram(fiber_dict[tid],
                         reference=brain_mask,
                         space=Space.RASMM)

sft.to_vox()

brain_mask_data = brain_mask.get_fdata()

scene = window.Scene()
scene.background((1, 1, 1))

# Display glass brain
brain_actor = actor.contour_from_roi(brain_mask_data, color=[0, 0, 0], opacity=0.05)
scene.add(brain_actor)

arc_actor = lines_as_tubes(sft.streamlines, 8, opacity=0.1)
scene.add(arc_actor)

window.show(scene, size=(1200, 1200), reset_camera=False)