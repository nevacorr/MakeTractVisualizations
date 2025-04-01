import h5py
import os.path as path
import scipy.io
import nibabel as nib
import numpy as np



mat_dir = '/Users/neva/AFQ_data'
mat_file = 'fiberfiles_genz323.mat'

mat_data = scipy.io.loadmat(path.join(mat_dir, mat_file))

fg=mat_data['fg']

# Print the type and contents of 'fg'
print(type(fg))
# If 'fg' is a structured array, you can list its fields
if fg.dtype.names:
    print(fg.dtype.names)

fibers= fg['fibers']

names = fg['name'] # tract region name

# Create an identity matrix affine (no transformation)
# Would be better to include a real affine
identity_affine = np.eye(4)

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

    row_name = str(names[i][0])  # Extract name safely
    row_name = row_name.replace(' ', '_')[:100]  # Clean and shorten filename

    trk_filename = f"{row_name}.trk"

    # Create Tractogram object
    tractogram = nib.streamlines.Tractogram(streamline_sequence, affine_to_rasmm=identity_affine)

    # Save to .trk file
    nib.streamlines.save(tractogram, trk_filename)
    print(f"Saved fibers for {row_name} to {trk_filename}")
    mystop=1