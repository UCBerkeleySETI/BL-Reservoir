# BL-Reservoir
BL Reservoir is a repository of tools we've developed to search through our data in new and different ways. Algorithms developed will be packaged into a docker image, and made avaliable for execution on cloud GCP's cloud computing platform to scale SETI searches. To trigger the execution of various algorithms, BL@Scale facilitates the scaling of such products.

## Packaging Your Code

First we need you to create a single executable python script to run when the kubernetes pods get triggered to process your data. An example of this is the Energy Detection Algorithm.
It contains two scripts of interest, `preprocess_fine.py` and `energy_detection.py`. The `energy_detection.py` is the script that's ran when the kubernetes pods are triggered and it manages the 
data used for the `preprocess_fine.py` which is then called on. 

You can see this in the `energy_detection.py` where it runs the following line

```
fail = os.system(f"cd alien_hunting_algs/energy_detection && python3 preprocess_fine.py {os.path.join(os.getcwd(), filename)}")
```
