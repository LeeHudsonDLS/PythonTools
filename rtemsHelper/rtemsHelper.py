import sys
import os

def convertDLS8515(original):

    output = ""

    params = original.split(',')
    portOrig = original.split('"')[1]
    port = portOrig[1:].replace('/','_')
    baud = params[1].strip()
    bits = params[2].strip()
    stop = params[3].strip()
    parity = params[4].strip().replace("'","")
    crtscts = params[5].split("'")[1]
    if parity == 'E':
        parity = "even"

    output +=f'#{port}\n'
    output +=f'asynSetOption("{port}",0,"baud","{baud}")\n'
    output +=f'asynSetOption("{port}",0,"bits","{bits}")\n'
    output +=f'asynSetOption("{port}",0,"parity","{parity}")\n'
    output +=f'asynSetOption("{port}",0,"stop","{stop}")\n'
    output +=f'asynSetOption("{port}",0,"crtscts","{crtscts}")\n'
    output +=f'asynSetOption("{port}",0,"clocal","Y")\n\n'

    return output

def createVariable(fmat,vals):

    vals = f'({vals})'
    cmd = f"a='{fmat}' % {vals}"
    exec(cmd)
    return locals()['a']

def addIpac(args):
    test = 1
    return f'ipacAddHy8002("{args.split()[0]},2")\n'



fileName = f'{os.getcwd()}/{sys.argv[1]}'

file = open(fileName, "r")
contents = file.readlines()
file.close()
vars = dict()
availableVects = [240 + i for i in range(10)]
usedVects = list()
IPACList = list()

for i,line in enumerate(contents):
    if "DLS8515DevConfigure" in line:
        contents[i] = convertDLS8515(line)
    if "sprintf" in line:
        varName = line.split(',')[0].split('(')[-1]
        fmat = line.split('"')[1]
        vals = line.split('"')[2].split(')')[0][1:].replace(' ','')
        if 'IVEC' in vals:
            vals = vals.replace('IVEC',str(availableVects[0]))
            usedVects.append(availableVects.pop(0))
            vars[varName] = createVariable(fmat,vals)
    if "ipacEXTAddCarrier" in line:
        contents[i] = addIpac(vars['ARGS'])
        IPACList.append(vars['ARGS'][0])
    else:
        for j,IPAC in enumerate(IPACList):
            if f'IPAC{IPAC}' in line:
                contents[i] = contents[i].replace(f'IPAC{IPAC}',f'$(Carrier{j})')




file = open(fileName, "w")            
file.writelines(contents)
file.close()