
import tensorflow as tf
import pandas as pd
from DeepSeti import DeepSeti
import os 
import sys


if __name__ == "__main__":
  input_file = sys.argv[1]

  if len(sys.argv) == 2:
      out_dir = input_file.split(".")[0]
  else:
      out_dir = sys.argv[2]
  if not os.path.isdir(out_dir):
        os.mkdir(out_dir)

  DeepSeti = DeepSeti()
  print(input_file)
  print("Loading model weights")
  DeepSeti.load_model_function('encoder_injected_model_Cudda.h5')
  print("Loading Anchor ")
  DeepSeti.load_anchor_npy('anchor.npy')
  print("running search")
  DeepSeti.prediction_numpy(test_location=input_file, 
                  top_hits=100,
                  target_name=input_file, 
                  output_folder=out_dir,
                  numpy_folder= out_dir)
  print("search complete")
