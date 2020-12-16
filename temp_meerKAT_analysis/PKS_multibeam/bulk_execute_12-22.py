import os
import sys

input_file = str(sys.argv[1])
file_name = str(sys.argv[2])
print(input_file)
nodes = [12,13,14,15,16,17]
for i in nodes:
    print(' /home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/data/'+str(file_name)+'/blc0'+str(i)+"/")
    os.system('python3 energy_detection_fine_PKS.py '+input_file + ' /home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/PKS_multibeam/'+str(file_name)+'/blc0'+str(i)+"/")
    if i<9:
        input_file = input_file.replace('blc0'+str(i), 'blc0'+str(i+1))
    else:
        input_file = input_file.replace('blc'+str(i), 'blc'+str(i+1))