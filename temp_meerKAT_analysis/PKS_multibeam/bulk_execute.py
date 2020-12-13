import os
import sys

input_file = str(sys.argv[1])
print(input_file)
for i in range(1, 31):
    print(' /home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/data' +input_file.replace('/mnt_blpd11/datax2/collate_mb/PKS_0371_2018-10-19T02:00/blc01/', '')+'/blc0'+str(i))
    os.system('python3 energy_detection_fine.py '+input_file + ' /home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/data'+input_file.replace('/mnt_blpd11/datax2/collate_mb/PKS_0371_2018-10-19T02:00/blc01/','')+'/blc0'+str(i))
    if i<9:
        input_file = input_file.replace('blc0'+str(i), 'blc0'+str(i+1))
    else:
        input_file = input_file.replace('blc'+str(i), 'blc'+str(i+1))
