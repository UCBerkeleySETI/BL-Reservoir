import numpy as np
import pandas as pd

import sys
import os


if __name__ == "__main__":
    input_file = sys.argv[1]
    if len(sys.argv) == 2:
        out_dir = input_file.split(".")[0]
    else:
        out_dir = sys.argv[2]

    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        
    df = pd.read_pickle(input_file)
    df.head().to_pickle(out_dir + "/df_head.pkl")
