import sys
import os






class rtemsHelper():
    def __init__(self):

        fileName = f'{os.getcwd()}/{sys.argv[1]}'

        file = open(fileName, "r")
        self.contents = file.readlines()
        file.close()
        self.vars = dict()
        self.availableVectsVals = [240 + i for i in range(10)]
        self.availableVectsMacro = [f'$(Vect{i})' for i in range(10)]
        self.availableVects = [v.replace('$','') for v in self.availableVectsMacro]
        self.availableVects = [v.replace('(','') for v in self.availableVects]
        self.availableVects = [v.replace(')','') for v in self.availableVects]
        self.usedVects = list()
        self.IPACList = list()


        for i,line in enumerate(self.contents):
            if "DLS8515DevConfigure" in line:
                self.contents[i] = self.convertDLS8515(line)
            if "newInterruptVector" in line:
                if '=' in line:
                    varName = line.split('=')[0].replace('$(VXWORKS_ONLY)','').strip()
                    self.vars[varName] = self.getNewInterruptVector()
                    self.contents[i] = f'#{line}'
                    print("Here")
                else:
                    print("Here")

            if "sprintf" in line:
                varName = line.split(',')[0].split('(')[-1]
                fmat = line.split('"')[1]
                vals = line.split('"')[2].split(')')[0][1:].replace(' ','')
                self.vars[varName]=self.createVariable(fmat,vals)
                for var in self.vars.keys():
                    if var in vals:
                        vals = vals.replace(var,self.vars[var])
                self.contents[i] = f'#{line}'
            if "ipacEXTAddCarrier" in line:
                self.contents[i] = self.addIpac(self.vars['ARGS'])
                self.IPACList.append(self.vars['ARGS'][0])
            else:
                for j,IPAC in enumerate(self.IPACList):
                    if f'IPAC{IPAC}' in line:
                        self.contents[i] = self.contents[i].replace(f'IPAC{IPAC}',f'$(Carrier{j})')

                # Sort dict in reverse order so longer strings appear        
                self.vars = dict(sorted(self.vars.items(), reverse = True))
                for var in self.vars.keys():
                    if var in line:
                        self.contents[i] = self.contents[i].replace(var,self.vars[var])
            
        for i in range(10,-1,-1):
            self.contents.insert(0,f'epicsEnvSet("Carrier{i}","{i}")\n')

        # Print epicsEnvSets
        for v,m in zip(self.availableVectsVals[::-1],self.availableVects[::-1]):
            self.contents.insert(0,f'epicsEnvSet("{m}", "{v}")\n')      

        file = open(fileName, "w")            
        file.writelines(self.contents)
        file.close()

    def getNewInterruptVector(self):
        interruptMacro = self.availableVectsMacro[0]
        self.usedVects.append(self.availableVectsMacro.pop(0))
        return interruptMacro

    def convertDLS8515(self,original):

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

    def createVariable(self,fmat,vals):

        substitutionList = list()

        for var in self.vars.keys():
            for i,sub in enumerate(vals.split(',')):
                if var in sub:
                    substitutionList.append(i)
                    vals = vals.replace(var,f"self.vars['{var}']")

        fmat = fmat.split()
        for sub in substitutionList:
            fmat[sub] = '%s'

        fmat = ' '.join(fmat)

        vals = f'({vals})'
        cmd = f"a='{fmat}' % {vals}"
        exec(cmd)
        return locals()['a']

    def addIpac(self,args):
        test = 1
        return f'ipacAddHy8002("{args.split()[0]},2")\n'


if __name__ == "__main__":
    a = rtemsHelper()


