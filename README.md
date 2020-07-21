# BL-Reservoir
BL Reservoir is a repository of tools we've developed to search through our data in new and different ways. Algorithms developed will be packaged into a docker image, and made avaliable for execution on cloud GCP's cloud computing platform to scale SETI searches. To trigger the execution of various algorithms, BL@Scale facilitates the scaling of such products.

## Connecting Your Code

First we need you to create a single executable python script to run when the kubernetes pods get triggered to process your data. An example of this is the Energy Detection Algorithm.
It contains two scripts of interest, `preprocess_fine.py` and `energy_detection.py`. The `energy_detection.py` is the script that's ran when the kubernetes pods are triggered and it manages the 
data used for the `preprocess_fine.py` which is then called on. 
You can see this in the `energy_detection.py` where it runs the following line

```
fail = os.system(f"cd alien_hunting_algs/energy_detection && python3 preprocess_fine.py {os.path.join(os.getcwd(), filename)}")
```
The `preprocess_fine.py` script actually does the "searching" whereas the `energy_detection.py` script facilitates the connection for the search. 

**Everything else about the script will be the same for all algorithms doing a search**.

### Uploading Results From Your Code
Let's say you've ran your code, how does it get uploaded so we can see the results? Well in the same `energy_detection.py` script the entire directory of which the results are saved in the instance are uploaded to the BL-Scale Google Storage bucket. This will then be displayed on the front end. 
```
upload.upload_dir("bl-scale", os.path.join(os.getcwd(), obs_name))
```

## Packaging the Code

Now lets say you want to write the algorithm to search. How do you format it to work with this setup? Simply write the script like any other python script, but make sure to include a system argument that lets us pass in our data in! From the `preprocess_fine.py` example, you can see it accepts a system argument, and then creates an out directory for the results. 

```
if __name__ == "__main__":
  input_file = sys.argv[1]
      if len(sys.argv) == 2:
          out_dir = input_file.split(".")[0]
      else:
          out_dir = sys.argv[2]
```

This results directory is important as this will be whats uploaded to the storage buckets. 

### Format of Results 
If you want the results to be displayed on the front end, it should follow this standard format.
- `NumPy` Stack of the results ideally named `filtered.npy`
- Corresponding info to each of the hits in a pandas dataframe saved in a pickled format `info_df.pkl`
- Header info saved in a pickled format
This allows the front end to then display each result from the results. 

The rest of the algorithm is for you to play with. 

### Dockerfile
The dockerfile is where the magic happens. We will containerize all the "stuff" needed to run your algorithm. From the Energy Detection Dockerfile we have the following.

```
FROM kernsuite/base:dev

USER root

ENV DEBIAN_FRONTEND=noninteractive

# install base dependencies
RUN docker-apt-install \
     python3-setuptools \
     python3-scipy \
     python3-matplotlib \
     python3-bitshuffle \
     python3-h5py \
     python3-pip \
     git \
     curl
RUN pip3 install zmq tqdm pandas wget google-cloud-storage hdf5plugin

RUN mkdir /code
WORKDIR /code


COPY . /code/bl_reservoir

CMD python3 -m bl_reservoir.$ALG_SUB_PACKAGE.$ALG_NAME
```

The only thing that will change between your algorithm is the requirements you need to run your script. Everything else would be setup for you to run your code. Which means
you just need to change this line below to whatever requirements you need for your algorithm. 
```
RUN pip3 install zmq tqdm pandas wget google-cloud-storage hdf5plugin
```

## Deploying Your Work

After you've done all the work above and packaged things together nicely, the code would be automatically uploaded to Dockerhub where the images can be ran on the GCP instances. 

However, inorder to get your changes to show, you'd need to be able restart the kubernetes cluster by using `Google SDK` login with proper credentials and proper project, you would be able to run `kubectl get pods` and then `kubectl rollout restart ds bl-scale` it would restart the kubernetes cluster to contain the new image you just pushed on github which is held in the registry 

# Questions

Feel free to the BL-Scale team about how this works. We'll help you out on running this at scale. 
