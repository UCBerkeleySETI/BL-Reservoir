import time
import sys
import os

out_dir = sys.argv[2]

print(out_dir)
time.sleep(30)

with open(os.path.join(out_dir, "called_time.txt"), "w") as f:
    f.write(str(time.time()*1000))
