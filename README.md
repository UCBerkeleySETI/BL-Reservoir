# BL-Reservoir
BL Reservoir is a repository of tools we've developed to search through our data in new and different ways. Algorithms developed will be packaged into a docker image, and made avaliable for execution on GCP's cloud computing platform to scale SETI searches. To trigger the execution of various algorithms, BL@Scale facilitates the scaling of such products.

## Adding Your Environment

Users will need to add their own sub-directory containing a `requirements.txt` file to specify their Python environment. Our `setup_environments.sh` script will make a Python virtual environment inside your sub-directory when the docker image builds. e.g. `energy_detection/requirements.txt` will generate a virtual environment located in `energy_detection/energy_detection_env`.

## Packaging the Code

Now lets say you want to write the algorithm to search. How do you format it to work with this setup? Simply write the script like any other python script, but make sure to include a system argument that lets us pass in our data in! From the `preprocess_fine.py` example, you can see it accepts a system argument, and then creates an out directory for the results. 

```
if __name__ == "__main__":
  input_file = sys.argv[1]
      if len(sys.argv) == 2:
          out_dir = input_file.split(".")[0]
      else:
          out_dir = sys.argv[2]
      if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
```

This results directory is important as this will be whats uploaded to the storage buckets. 

You code will be called as a command line utility in the form of `python3 script.py <input_file> <output_directory>` inside the compute pod. Currently, we require your code to conform to this interface, but we'll have a more flexible interface in the future.

### Uploading Results From Your Code
Let's say you've ran your code, how does it get uploaded so we can see the results? We use [FUSE mounts](https://cloud.google.com/storage/docs/gcs-fuse) to allow your code to write directly to our public accesible storage bucket, [bl-scale](https://console.cloud.google.com/storage/browser/bl-scale).

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

After you've done all the work above and packaged things together, the code would be automatically uploaded to the registry after you push to the repo where the images can be ran on the GCP instances. 

However, in order to get your changes to show, you'd need to restart the kubernetes cluster by using `Google SDK` login with proper credentials and navigating to the project BL-Sandbox project, you would be able to run `kubectl get pods` and then `kubectl rollout restart ds bl-scale` it would restart the kubernetes cluster with the new image you just pushed on github which is held in the BL@Scale registry. 

# Questions

Feel free to reach out to the BL-Scale team about how this works. We'll help you out on running this at scale. 

