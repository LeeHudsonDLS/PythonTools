from subprocess import Popen, PIPE, check_output
import argparse

def send_message(recipient, subject, body):
    process = Popen(['mail', '-s', subject, recipient],stdin=PIPE)
    process.communicate(body.encode())

parser = argparse.ArgumentParser()
parser.add_argument('-a',dest="area",nargs='?', help="String describing which area of IOCs you want to search: FE,SR,BR", default="SR")
args=parser.parse_args()


logPath = "/dls/ops-data/epics/logs/"
message = ""
subject = ""
removeColSED = "sed 's/\x1B\[[0-9;]\{1,\}[A-Za-z]//g'"
removeChar = 'tr -cd "[:print:]"'

iocSuffix = "I"
iocType = "CS"



if args.area == "SR":
    iocSuffix = "C"
    iocType = "VA"
    subject = "SR IOC console report\n"
    
    for ioc in range(1,24):
        message+= f"Logs for {args.area}{ioc:02d}{iocSuffix}-{iocType}-IOC-01"
        stdout = Popen(f"tail -5 {logPath}{args.area}{ioc:02d}{iocSuffix}-{iocType}-IOC-01/console.log | {removeColSED} | {removeChar}",shell=True,stdout=PIPE).stdout.read().decode()            
        message+=stdout
        message+= f"\n"
        message+= f"\n"

if args.area == "BR":
    iocSuffix = "C"
    iocType = "VA"
    subject = "BR IOC console report\n"
    
    for ioc in range(1,5):
        message+= f"Logs for {args.area}{ioc:02d}{iocSuffix}-{iocType}-IOC-01"
        stdout = Popen(f"tail -5 {logPath}{args.area}{ioc:02d}{iocSuffix}-{iocType}-IOC-01/console.log | {removeColSED} | {removeChar}",shell=True,stdout=PIPE).stdout.read().decode()            
        message+=stdout
        message+= f"\n"
        message+= f"\n"

if args.area == "FE":
    iocSuffix = "C"
    iocType = "VA"
    subject = "FE IOC console report\n"
    feIOCS = ["FE02I-CS-IOC-01",
              "FE02J-CS-IOC-01",
              "FE03I-CS-IOC-01",
              "FE04I-CS-IOC-01",
              "FE05I-CS-IOC-01",
              "FE06I-CS-IOC-01",
              "FE07I-CS-IOC-01",
              "FE08I-CS-IOC-01",
              "FE09I-CS-IOC-01",
              "FE10I-CS-IOC-01",
              "FE10B-CS-IOC-01",
              "FE11I-CS-IOC-01",
              "FE11K-CS-IOC-01",
              "FE12I-CS-IOC-01",
              "FE13I-CS-IOC-01",
              "FE14I-CS-IOC-01",
              "FE15I-CS-IOC-01",
              "FE16I-CS-IOC-01",
              "FE16B-CS-IOC-01",
              "FE18I-CS-IOC-01",
              "FE18B-CS-IOC-01",
              "FE19I-CS-IOC-01",
              "FE20I-CS-IOC-01",
              "FE21I-CS-IOC-01",
              "FE21B-CS-IOC-01",
              "FE22I-CS-IOC-01",
              "FE22B-CS-IOC-01",
              "FE23I-CS-IOC-01",
              "FE23B-CS-IOC-01",
              "FE24I-CS-IOC-01",
              "FE24B-CS-IOC-01",]
    
    for ioc in feIOCS:
        message+= f"Logs for {ioc}"
        stdout = Popen(f"tail -5 {logPath}{ioc}/console.log | {removeColSED} | {removeChar}",shell=True,stdout=PIPE).stdout.read().decode()            
        message+=stdout
        message+= f"\n"
        message+= f"\n"        


#Make it more readable
message = message.replace("[","\n[")        

send_message("lee.hudson@diamond.ac.uk",subject,message)