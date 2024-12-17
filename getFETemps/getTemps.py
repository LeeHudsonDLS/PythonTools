
import os
from subprocess import Popen, PIPE

results = dict()
iocs = list()

iocs.append("FE02I-CS-IOC-01")
iocs.append("FE02J-CS-IOC-01")
iocs.append("FE07B-CS-IOC-01")
iocs.append("FE08I-CS-IOC-01")
iocs.append("FE10B-CS-IOC-01")
iocs.append("FE11K-CS-IOC-01")
iocs.append("FE14I-CS-IOC-01")
iocs.append("FE15I-CS-IOC-01")
iocs.append("FE21I-CS-IOC-01")
iocs.append("FE24B-CS-IOC-01")

getcal = 'GETCALC\") {'
grepString = f'grep -nr \'{getcal}\' ' 

for ioc in iocs:
    print(ioc)
    redirector_1 = Popen(f"configure-ioc s {ioc}",shell=True,stdout=PIPE).stdout.read().decode().split('bin')[0]
    dbDirectory = f'{redirector_1.split()[-1]}db'
    grepString = f'{grepString} {dbDirectory}'
    grepResults = Popen(f'{grepString}',shell=True,stdout=PIPE).stdout.read().decode().split('\n')
    grepResults.pop()
    for grepResult in grepResults:
        pv = grepResult.split('"')[1]
        result = Popen(f"caget {pv}",shell=True,stdout=PIPE).stdout.read().decode().split()
        results[result[0]]=result[1]


for key,value in results.items():
    print(key, '->', value)