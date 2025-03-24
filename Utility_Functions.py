
import pandas as pd
import numpy as np

def load_data(filepath, filename):
    df = pd.read_csv(f"{filepath}{filename}")

    z = df.loc[df["Tract"] == "Left.Arcuate", "Z_mean"].values
    adjp = df.loc[df["Tract"] == "Left.Arcuate", "adjusted_p_value"].values

    mean_z_value = np.mean(z)

    z_segment_to_add = np.full(20, mean_z_value)
    p_segment_to_add = np.full(20, 1.0)

    z_final = np.concatenate([z_segment_to_add, z, z_segment_to_add])
    p_final = np.concatenate([p_segment_to_add, adjp, p_segment_to_add])

    return z_final, p_final