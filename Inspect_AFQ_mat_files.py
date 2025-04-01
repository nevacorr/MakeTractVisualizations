import h5py
import os.path as path
import scipy.io

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


# Inspect the first few elements of fibers
for i in range(fibers.shape[1]):
    print(f"Fiber {i+1}:")
    print(fibers[0, i])  # Access the element in the 1st row and ith column
    print(f"Shape: {fibers[0, i].shape}")

# Access a specific fiber (e.g., the first fiber)
fiber_1 = fibers[0, 0]  # First element (fiber)
print(f"Fiber 1 shape: {fiber_1.shape}")
print(fiber_1)  # Print the fiber data

# If the fiber is a list or array of arrays, you can access the individual arrays inside it
for idx, array in enumerate(fiber_1):
    print(f"Array {idx+1} in Fiber 1: {array}")
    print(f"Shape: {array.shape}")

# Loop through each fiber to inspect the arrays inside it
for i, fiber in enumerate(fibers[0]):
    print(f"Fiber {i+1}:")
    for j, subarray in enumerate(fiber):
        print(f"  Subarray {j+1}: Shape {subarray.shape}")
        print(subarray)  # or use subarray[:5] to print only the first few elements






mystop=1