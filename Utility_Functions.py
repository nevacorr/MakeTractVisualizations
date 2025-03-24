
import pandas as pd
import numpy as np

def load_data(filepath, filename):
    df = pd.read_csv(f"{filepath}{filename}")

    z = df.loc[df["Tract"] == "Left.Arcuate", "Z_mean"].values
    adjp = df.loc[df["Tract"] == "Left.Arcuate", "adjusted_p_value"].values

    return z, adjp