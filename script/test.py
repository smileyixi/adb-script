import os
import subprocess
from adb import Adb_func
print(subprocess.getoutput(Adb_func.showAllPkg("--this")).split(" ")[-1].split("/")[0])