import csv
import time 
import sys 
import os
from os import listdir
from os.path import isfile, join

directory_listen = str(sys.argv[1]) # file directory you want the computer to listen to. 
node_number = str(sys.argv[2]) # Node for the compute to make the proper output directory

def list_directory(mypath):
    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    for i in onlyfiles:
        if '.h5' in i:
            continue
        else:
            i = 'ignore'
    return onlyfiles

def newest(list_1,list_2):
    return list_2[len(list_1)]

original_list = list_directory(directory_listen)
while True:
    new_list = list_directory(directory_listen)
    if len(new_list) > len(original_list) and newest(original_list,new_list)[0] != 'ignore':
        diff = newest(original_list,new_list)
        print("Update Detected: Executing Run "+str(diff))
        try:
            os.mkdir(str(diff)+'_'+node_number)
        except:
            print("Couldn't make directory "+str(diff))
        print("python3 energy_detection_fine_4k.py "+ str(directory_listen)+ "/"+str(diff) +" "+str(diff)+'/'+node_number+ " "+ str(diff))
        os.system("python3 energy_detection_fine_4k.py "+ str(directory_listen)+ "/"+str(diff) +" "+str(diff)+'/'+node_number+ " "+ str(diff))
    else:
        print("No Update----------------")
        time.sleep(3)
    original_list = new_list
