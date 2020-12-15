import csv
import time 
import sys 
import os

input_line = str(sys.argv[1])
file_listener = str(sys.argv[2])
def open_csv(file):
    file_names= []
    with open(file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            file_names.append(row)
    return file_names

def difference(list_1,list_2):
    diff = []
    for i in list_2:
        if i in list_1:
            continue
        else:
            diff.append(i)
    return diff

original_list = None
while True:
    new_list = open_csv('file_listener')
    if new_list != original_list:
        diff = difference(original_list,new_list)
        print("Update Detected: Executing Run "+str(diff[0]))
        if input_line ==1:
            file_path = '/mnt_blpd11/datax2/collate_mb/PKS_0371_2018-10-19T02:00/*/'+str(diff[0])
            os.system("bulk_execute_1-11.py "+file_path+" "+str(diff[0]))
        elif input_line ==2:
            file_path = '/mnt_blpd11/datax2/collate_mb/PKS_0371_2018-10-19T02:00/*/'+str(diff[0])
            os.system("bulk_execute_1-11.py "+file_path+" "+str(diff[0]))
        elif input_line ==3:
            file_path = '/mnt_blpd11/datax2/collate_mb/PKS_0371_2018-10-19T02:00/*/'+str(diff[0])
            os.system("bulk_execute_1-11.py "+file_path+" "+str(diff[0]))
        else:
            print("wrong compute node")
        original_list = new_list     
    else:
        time.sleep(20)


