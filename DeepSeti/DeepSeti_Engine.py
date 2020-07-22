import pandas as pd
from DeepSeti import DeepSeti
import os 
import sys

if __name__ == "__main__":
  input_file = sys.argv[1]
  print(input_file)
  if len(sys.argv) == 2:
      out_dir = input_file.split(".")[0]
  else:
      out_dir = sys.argv[2]

  DeepSeti = DeepSeti()
  print(input_file)
  DeepSeti.load_anchor_npy('encoder_injected_model_Cudda.h5')
  DeepSeti.load_anchor_npy('anchor.npy')
  DeepSeti.prediction_numpy(test_location=input_file, 
                  top_hits=1,
                  target_name=input_file, 
                  output_folder=out_dir)
