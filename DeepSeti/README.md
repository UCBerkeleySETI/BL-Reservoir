# DeepSeti - Semi-Unsupervised SETI Search Tool
### Written by Peter Ma | [Contact](https://peterma.ca)
This is a python implementation of DeepSeti - an algorithm designed to detect anomalies for radio telescope data open sourced by Breakthrough Listen. These python scripts facilitates the custom architecture and training loops required for the DeepSeti algorithm to preform a multichannel search for anomalies. Main objective is to develop software that increases the computational sensitivity and speed to search for 'unknown' anomalies.  **NOTE:** *Currently this code only works for **MID-RES filterbank and h5 files**.*


# Introduction

The purpose of this algorithm is to help detect anomalies within the GBT dataset from Breakthrough Listen. The code demonstrates a potential method in accelerating ML SETI in large unlabeled datasets. This approach is an extension from the original paper [https://arxiv.org/pdf/1901.04636.pdf] by looking into preforming the final classification on the encoded feature vector by taking a triplet loss between an anchor, and positive or negative samples.


# Deep Learning Architecture

What makes this algorithm unique is that it *injects* an encoder, thats been previously trained on a classification dataset, into an autoencoder trained through unsupervised techniques. This method relies on a inital small labeled dataset where it is intermediately trained a CNN-LSTM classifier then injected it into the CNN-LSTM Auto Encoder. 

**Rationale**: The goal is to force the feature selection from CNN's to search for those desired labels while the unsupervised method gives it the “freedom” to familiarize with "normal data" and detect novel anomalies beyond the small labeled dataset. Both the supervised and unsupervised models are executed together and model injections occur intermittently.

*Reference diagram below*

<p align="center"> 
    <img src="https://github.com/PetchMa/DeepSeti/blob/master/assets/image%20(3).png">
</p>





