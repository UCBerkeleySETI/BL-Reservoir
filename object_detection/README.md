### Installation

Before using requirements.txt to install packages, run the following command first to install pytorch
    
    conda install pytorch torchvision -c pytorch

### Algorithm 

In order to run object_detection.py, pass in the following parameters in sequence: energy detection output + index of the sample + iou threshold. An example is shown below:

    python object_detection.py GBT_57803_83207_HIP3876_midfiltered.npy 10 0.1

Here the energy detection output are of window size 256

The algorithm will output a pickle file containing the detected boxes after nms and corresponding scores

### Plotting

To visualize the samples and the detection boxes, use the jupyter notebook