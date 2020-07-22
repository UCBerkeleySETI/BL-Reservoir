import wget
import pandas as pd
import requests
from DeepSeti import DeepSeti
import os 
import sys

if __name__ == "__main__":
  input_file = sys.argv[1]
  if len(sys.argv) == 2:
      out_dir = input_file.split(".")[0]
  else:
      out_dir = sys.argv[2]

  DeepSeti = DeepSeti()

  DeepSeti.load_anchor('anchor.npy')
  DeepSeti.prediction(model_location='encoder_injected_model_Cudda.h5', 
                  test_location=input_file, 
                  top_hits=100,
                  target_name=input_file, 
                  output_folder=out_dir)
