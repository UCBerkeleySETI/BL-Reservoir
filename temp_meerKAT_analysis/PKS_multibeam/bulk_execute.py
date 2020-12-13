import os
import sys

input_file = str(sys.argv[1])
print(input_file)
for i in range(1, 31):
    print(' /home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/data/' +'/blc0'+str(i))
    os.system('python3 energy_detection_fine_PKS.py '+input_file + ' /home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/data/'+'/blc0'+str(i)+"/")
    if i<9:
        input_file = input_file.replace('blc0'+str(i), 'blc0'+str(i+1))
    else:
        input_file = input_file.replace('blc'+str(i), 'blc'+str(i+1))
  File "energy_detection_fine.py", line 41, in <module>
    os.mkdir(out_dir)
FileNotFoundError: [Errno 2] No such file or directory: '/home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/data/blc01/guppi_58410_24817_190720_G337.28+6.26_0001.0000.h5/blc01'
 /home/pma/peterma-remote/BL-Reservoir/temp_meerKAT_analysis/data/blc02/guppi_58410_24817_190720_G337.28+6.26_0001.0000.h5/blc02
Traceback (most recent call last):