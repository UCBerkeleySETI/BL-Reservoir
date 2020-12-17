import csv
import time 
import sys 
import os

input_line = str(sys.argv[1])
def open_csv(file):
    file_names= []
    with open(file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            file_names.append(row)
    return file_names

def difference(list_1,list_2):
    return list_2[len(list_1)]

original_list = open_csv('file_listener.csv')
while True:
    new_list = open_csv('file_listener.csv')
    if len(new_list) > len(original_list):
        diff = difference(original_list,new_list)[0]
        print("Update Detected: Executing Run "+str(diff))
        try:
            os.mkdir(str(diff))
        except:
            print("Couldn't make directory "+str(diff))
        if int(input_line) ==1:
            print("computing node: "+str(input_line))
            file_path = '/mnt_blpd11/datax2/collate_mb/PKS_0371_2018-10-19T02:00/blc01/'+str(diff)
            print("python3 bulk_execute_1-11.py "+file_path+" "+str(diff))
            os.system("python3 bulk_execute_1-11.py "+file_path+" "+str(diff))

        elif int(input_line) ==2:
            print("computing node: "+str(input_line))
            file_path = '/mnt_blpd11/datax2/collate_mb/PKS_0371_2018-10-19T02:00/blc12/'+str(diff)
            print("python3 bulk_execute_12-22.py "+file_path+" "+str(diff))
            os.system("python3 bulk_execute_12-22.py "+file_path+" "+str(diff))

        elif int(input_line) ==3:
            print("computing node: "+str(input_line))
            file_path = '/mnt_blpd11/datax2/collate_mb/PKS_0371_2018-10-19T02:00/blc23/'+str(diff)
            print("python3 bulk_execute_23-32.py "+file_path+" "+str(diff))
            os.system("python3 bulk_execute_23-32.py "+file_path+" "+str(diff))
        else:
            print("wrong compute node")
        original_list = new_list     
    else:
        print("No Update----------------")
        time.sleep(3)

# /home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/PKS_multibeam
