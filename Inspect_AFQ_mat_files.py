import scipy.io
import nibabel as nib
import numpy as np
import os.path as op

def Inspect_AFQ_mat_files(subj, working_dir):

    mat_dir = op.join(f'{working_dir}/{subj}/dti64trilin')
    mat_file = f'fiberfiles_{subj}.mat' # This was a file that I manually exported from matlab after loading the
                                        # AFQ output .mat file given to me for this subject MoriGroups_Cortex_clean_D5_L4.mat).
                                        # The original .mat file contained other variables and was in HDF5 format
    dti_img_file = 'bin/mpfcoreg12.nii.gz'

    # Load data
    mat_data = scipy.io.loadmat(op.join(mat_dir, mat_file))
    dti_space_img = nib.load(op.join(mat_dir, dti_img_file))

    # Extract image properties
    affine = dti_space_img.affine  # Get the affine transformation
    dims = dti_space_img.shape  # Get the voxel dimensions

    fg = mat_data['fg']
    fibers = fg['fibers']
    names = fg['name'] # tract region names

    for i in range(fibers.shape[1]):  # Loop over the 20 regions
        current_fibers = fibers[0, i]  # Extract the current region's fibers
        fiber_data = []

        for j in range(current_fibers.shape[0]):  # Loop over each fiber (streamline)
            fiber = current_fibers[j]  # Extract the current fiber

            # Check if fiber has the expected shape (1, N, 3), so access fiber[0] to get the actual data
            fiber_array = fiber[0]  # fiber[0] should now be the (N, 3) array with coordinates

            # Now extract x, y, z coordinates
            x = fiber_array[0, :]  # x coordinates
            y = fiber_array[1, :]  # y coordinates
            z = fiber_array[2, :]  # z coordinates

            # Combine x, y, and z arrays element-wise into a single (N, 3) array
            fiber_points = np.vstack([x, y, z]).T  # Stack vertically and transpose to get (N, 3)

            # Append the processed fiber points to fiber_data
            fiber_data.append(fiber_points)

        streamline_sequence = nib.streamlines.ArraySequence(fiber_data)

        # Clean up the filename
        row_name = str(names[0][i]).replace('[', '').replace(']', '').replace(' ', '_')[:100]
        trk_filename = f"{row_name}.trk"

        # Remove any additional quotes if they're present
        trk_filename = trk_filename.replace("'", "")

        # Create Tractogram object
        tractogram = nib.streamlines.Tractogram(streamline_sequence, affine_to_rasmm=affine)

        # Save to .trk file
        nib.streamlines.save(tractogram, op.join('new_trk_files', trk_filename))
        print(f"Saved fibers for {row_name} to {trk_filename}")
