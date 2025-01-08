#!/bin/env dls-python3

import sys
import re
from subprocess import Popen, PIPE
import argparse



parser = argparse.ArgumentParser()
parser.add_argument("file",nargs='?', help="Path to substitution file", default="/dls_sw/work/R3.14.12.7/ioc/SR20C/VA/SR20C-VA-IOC-01App/Db/SR20C-VA-IOC-01.substitutions")
args=parser.parse_args()

# List of non builder classes, need manual intervention
notSupported = list()

# Character to replace single spaces for to avoid them being stripped
subChar = '*'

needsNameField = ['mks937a','mks937b','mks937aGauge','mks937bGauge','digitelMpc','mks937bImg','mks937bPirg']
needsPortLookup = {'mks937aImg':'GCTLR',
                   'mks937aPirg':'GCTLR',
                   'mks937bImg':'GCTLR',
                   'mks937bPirg':'GCTLR',
                   'digitelMpcIonp':'MPC'}

needsDeviceLookup = {'mks937bRelays':'GAUGE',
                     'mks937bFastRelay':'GAUGE'}
asynPortDevice = ['mks937a','digitelMpc','mks937b']

# Uses original class name, not the one derived from classNameLookup
unusedFields = {'digitelMpcIonp':['unit'],
                'dlsPLC_read100':['fins_timeout'],
                'mks937bImg':['address','port'],
                'mks937bPirg':['address'],
                'mks937bRelays':['address','port','device'],
                'mks937bFastRelay':['address','port','device','channel'],
                'frontendValveSNL':['abdelay','fvdelay','absb'],
                'dlsPLC_feTemperature':['port'],
                'dlsPLC_vacValveTclose':['port'],
                'dlsPLC_vacPump':['valve','fins_timeout'],
                'dlsPLC_vacValveDebounce':['fins_timeout','tclose_hihi','tclose_hhsv','tclose_hsv','tclose_high'],
                'ChannelUn':['nelm','card','channel'],
                'MASTER':'PORT',
                'basic_motor':['RDBL','UREV'],
                'digitelMpcIonp':['spon','spoff','unit']}

autoClassList = ['Hy8401ip','rgaGroup','mks937aImgMean','Channel16',
                 'Channel8','ChannelUn','psu24vStatus','dlsPLC_CommsStatus',
                 'dlsPLC_feFastValve','frontendValveSNL','beamline_access',
                 'ValveSequencer','XBPMLookup','XBPMStats','pbpm_common',
                 'beam_geometry','BLFEControl','BLFEControl','dlsPLC_vacValveTclose',
                 'dlsPLC_digio','dlsPLC_radmonreset','motor_gui','dlsPLC_mpsPermit',
                 'valveArchiver','ValveSequencer','frontendValveSNL','dlsPLC_fvg',
                 'mks937aPlogADC', 'basic_motor', 'MotorSequencer','valveArchiver',
                 'record_alias','pbpm','beamline_access', 'asynRec'
                 ]

fieldNameLookup = {'evr_alive':{'SYSTEM':'device'},'DLS8512chan':{'name':'suffix'}}



# template name as it appears in subs : builder class name
classNameLookup = {'dlsPLC_read100':'read100',
                   'space':'spaceTemplate',
                   'space_b':'space_bTemplate',
                   'dlsPLC_vacValveDebounce':'vacValveDebounce',
                   'FINS':'FINSTemplate',
                   'flowmeter':'flowMeter',
                   'dlsPLC_vacValveGroup':'vacValveGroup',
                   'dlsPLC_vacPump':'vacPump',
                   'dlsPLC_feTemperature':'feTemperature',
                   'dlsPLC_feFastValve':'feFastValve',
                   'insulation_vac_space':'FE24B_insulation_vac_space',
                   'vacuumSpaceOverrides':'FE24B_vacuumSpaceOverrides',
                   'dig':'FE07I_dig',
                   'pbpm-common':'auto_pbpm_common',
                   'generalTime':'generalTimeTemplate',
                   'customCombGauge':'FE24B_customCombGauge',
                   'gadc':'GenericADCTemplate',
                   'MASTER':'MasterTemplate',
                   'pt100':'idPT100Template',
                   'enzLoCuM4':'enzLoCuM4',
                   'Hy8403ip':'Hy8403ipTemplate',
                   'VHS40x-chans':'VHS40xChans',
                   'my_evr':'auto_my_evr_FE07I'}


#{'ty_40_0':'GCTLR_S_01',
# 'ty_40_1':'GCTLR_A_01'}
portLookup = dict()


# Returns string describing the a suitable name for the device
def getName(instance,fileNameNoExt):
    name = ''
    if fileNameNoExt == 'mks937a' or fileNameNoExt == 'mks937b':
        device = instance.strip().split()[0]
        name = f"GCTLR_{device[4]}_{device[-2:]}"
    if fileNameNoExt == 'mks937bImg':
        device = instance.strip().split()[0]
        name = f"IMG_{device[4]}_{device[-2:]}"
    if fileNameNoExt == 'mks937bPirg':
        device = instance.strip().split()[0]
        name = f"PIRG_{device[4]}_{device[-2:]}"
    if fileNameNoExt == 'mks937aGauge' or fileNameNoExt == 'mks937bGauge':
        dom = instance.strip().split()[0]
        id = instance.strip().split()[1]
        name = f"GAUGE_{dom[-1]}_{id}"
    if fileNameNoExt == 'digitelMpc':
        device = instance.strip().split()[0]
        name = f"MPC_{device[4]}_{device[-2:]}"

    return name

def extractPattern(substitutionString,fileNameNoExt):

    removeFromPattern = ["pattern","{","}",","]
    patStart = substitutionString.find("pattern")
    patEnd = substitutionString.find('}')+1

    patternSubString  = substitutionString[patStart:patEnd]

    for token in removeFromPattern:
        patternSubString = patternSubString.replace(token,' ')

    if fileNameNoExt in needsPortLookup.keys():
        patternSubString = patternSubString.replace('port',needsPortLookup[fileNameNoExt])

    if fileNameNoExt in needsDeviceLookup.keys():
        patternSubString = patternSubString.replace('device',needsDeviceLookup[fileNameNoExt])

    pattern = patternSubString.split()
    if fileNameNoExt in needsNameField:
        pattern.insert(0,'name')



    return pattern

def replaceSingleQuotes(input):
    
    input = input.replace('""','*')
    input = input.replace('"','')
    input = input.replace('*','""')

    return input

# Returns list of stings describing the field values separated by whitespace, eg:
# result[0] = 'SR24S-VA-GCTLR-01   ty_40_0'
# result[1] = 'SR24S-VA-GCTLR-01   ty_40_1'
def extractInstancesIntoList(substitutionString,fileNameNoExt):


    removeFromInstance = ["\n","\t","}"]

    result = substitutionString.split('{')
    result = result[3:]
    for i, instance in enumerate(result):
        for token in removeFromInstance:
            instance = instance.replace(token,'')
        instance = replaceSingleQuotes(instance)
        instance = instance.replace(',','  ')
        instance = instance.replace('&', "&amp;")
        
        # Gets name field if needed
        name = getName(instance,fileNameNoExt)

        # Replace single spaces with subChar to avoid them getting stripped
        instance = re.sub(r'(?<=\S)\s(?=\S)',subChar,instance.strip())

        result[i]=f"{name} {instance.strip()}"
        

    return result

def getModuleName(templateName):

    # Support module : template name as it appears in substitution file
    builderClassLookup = {'mks937a':["mks937a","mks937aGauge","mks937aImg","mks937aPirg","mks937aGaugeGroup","mks937aImgGroup","mks937aPirgGroup","mks937aImgMean",'mks937aPlogADC'],
                          'mks937b':["mks937b","mks937bGauge","mks937bImg","mks937bPirg","mks937bRelays","mks937bFastRelay","mks937bGaugeGroup","mks937bImgGroup","mks937bPirgGroup","mks937bImgMean"],
                          'digitelMpc':["digitelMpc","digitelMpcIonp","digitelMpcTsp","digitelMpcIonpGroup","digitelMpcTspGroup","digitelMpcqTsp"],
                          'rga':["rga",'rgaGroup'],
                          'vacuumSpace':["space","space_b"],
                          'rackFan':["rackFan"],
                          'Hy8401ip':["Hy8401ip"],
                          'FastVacuum':["Master16","Channel16","Channel8","ChannelUn"],
                          'FINS':["FINS"],
                          'PT100':['pt100'],
                          'TimingTemplates':["defaultEVR",'generalTime','evr_alive'],
                          'SR-VA':["psu24vStatus"],
                          'ethercat':['gadc','MASTER'],
                          'Hy8403ip':['Hy8403ip'],
                          'dlsPLC':["dlsPLC_read100","dlsPLC_vacValveDebounce","dlsPLC_vacValveGroup","dlsPLC_CommsStatus","dlsPLC_feFastValve","dlsPLC_feTemperature","dlsPLC_vacValveTclose",'dlsPLC_radmonreset','dlsPLC_digio','dlsPLC_mpsPermit','dlsPLC_vacPump'],
                          'IOCinfo':["IOCinfo"],
                          'motor':['basic_motor'],
                          'FE':['motor_gui', 'MotorSequencer', 'FE24B_dig', 'asynRec', 'pbpm', 'valveArchiver', 'record_alias', 'XBPMStats', 'customCombGauge', 'vacuumSpaceOverrides', 'insulation_vac_space', 'BLFEControl', 'pbpm-common', 'beamline_access', 'flowmeter', 'dlsPLC_fvg', 'XBPMLookup', 'frontendValveSNL', 'beam_geometry', 'dig', 'ValveSequencer','my_evr'],
                          'enzLoCuM4':['enzLoCuM4'],
                          'DLS8512Templates':['DLS8512core','DLS8512chan'],
                          'vacuumValve':["vacuumValveGroup"],
                          'iseg-VHS40x':['VHS40x','VHS40x-chans']}

    for module in builderClassLookup:
        if templateName in builderClassLookup[module]:
            return module

    return ''

def getClassName(fileNameNoExt):


    
    if fileNameNoExt in autoClassList:
        return f"auto_{fileNameNoExt}"
    
    if fileNameNoExt in classNameLookup.keys():
        return classNameLookup[fileNameNoExt]
    
    return fileNameNoExt


def getPortElementNumber(instanceValues):
    for i, instance in enumerate(instanceValues):
        if 'ty_' in instance:
            return i
        if 'ts' in instance:
            return i
    return -1



fileInstanceDict = dict()


sub = args.file
substitutionFile = open(sub,'r')
lines = substitutionFile.readlines()
foundFile = False

fileInstance = ""
openBracketCounter = 0
closedBracketCounter = 0
templateFileName = ""

for line in lines:
    if line[0] != '#':

        if foundFile:
                fileInstance += line

        if "file" in line and not foundFile:
            templateFileName = line.split()[-1]
            foundFile = True
            fileInstance += line

        if foundFile:
            if '{' in line:
                openBracketCounter += 1
            if '}' in line:
                closedBracketCounter += 1

        if openBracketCounter > 0 and openBracketCounter == closedBracketCounter:
            
            if templateFileName not in fileInstanceDict.keys():
                fileInstanceDict[templateFileName]=fileInstance
            else:
                # Add to fileInstanceDict entry that already exists, ie, if a "file" is used multiple times in the substitution
                fileInstance = fileInstance.split('{')
                fileInstance.pop(0)
                fileInstance.pop(0)
                fileInstance.pop(0)

                # Remove last instance of '}' to allow insertion of more template instances (must be an easier way to do this....)
                lastBracket = fileInstanceDict[templateFileName].rfind('}')
                fileInstanceDict[templateFileName]=fileInstanceDict[templateFileName][:lastBracket] + '' + fileInstanceDict[templateFileName][lastBracket+1:]

                for f in fileInstance:
                    fileInstanceDict[templateFileName] += f'{{{f}'

                # Re-insert '}' at the end
                fileInstanceDict[templateFileName] += '}'
                

            foundFile = False
            openBracketCounter = 0
            closedBracketCounter = 0
            fileInstance = ""




for fileInstance in fileInstanceDict:
    template = fileInstanceDict[fileInstance]

    fileName=fileInstance
    fileNameNoExt=fileName.split('.')[0]

    patternList = extractPattern(template,fileNameNoExt)

    # Determine the field location of the port
    if fileNameNoExt in needsPortLookup:
        for i, field in enumerate(patternList):
            if patternList[i] == needsPortLookup[fileNameNoExt]:
                portElementNumber = i

    if fileNameNoExt in fieldNameLookup.keys():
        for i, field in enumerate(patternList):
            if field in fieldNameLookup[fileNameNoExt].keys():
                patternList[i] = fieldNameLookup[fileNameNoExt][field]

    if fileNameNoExt in needsDeviceLookup:
        for i, field in enumerate(patternList):
            if patternList[i] == needsDeviceLookup[fileNameNoExt]:
                portElementNumber = i

    instList = extractInstancesIntoList(template,fileNameNoExt)



    for instance in instList:
        className = getClassName(fileNameNoExt)
        xmlString = f"<{getModuleName(fileNameNoExt)}.{className} "
        instanceValues = instance.split()

        if fileNameNoExt in asynPortDevice:
            portLookup[instanceValues[getPortElementNumber(instanceValues)]] =  instanceValues[0]  

        if fileNameNoExt in needsPortLookup.keys():
            instanceValues[portElementNumber] = portLookup[instanceValues[portElementNumber]]

        if fileNameNoExt in needsDeviceLookup.keys():
            if instance.find(':',0,25)!= -1:
                basePv = instance.split(':')[0].strip()
            else:
                basePv = instance.split()[0].strip()
            deviceNo = basePv[-2:]
            typ=basePv[4]
            deviceType = basePv.split('-')[-2]
            instanceValues[portElementNumber] = f"{deviceType}_{typ}_{deviceNo}"

        if fileNameNoExt in unusedFields.keys():
            for i, field in enumerate(patternList):
                if patternList[i] in unusedFields[fileNameNoExt]:
                    patternList[i] = ''
                    instanceValues[i] = ''

        for i,p in zip(instanceValues,patternList):
            if len(p) > 0:
                temp = i.replace(subChar,' ')
                xmlString += f'{p}="{temp}" '
        xmlString += "/>"
        xmlString = xmlString.replace('""""','""')
        if(xmlString[1] == '.'):
            notSupported.append(xmlString)
        else:
            print(f"\t{xmlString}")


print("\nNot supported: ")
for instance in notSupported:
    print(instance)
