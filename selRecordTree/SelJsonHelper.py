
from cothread.catools import caget, camonitor, caput
import json

class SelJsonHelper:
    def __init__(self,pvs):
        self.pvs = pvs
        self.tree = dict()
        self.level = 0
        self.maxLevel = 0

        if isinstance(pvs,list):
            for pv in pvs:
                self.tree = {**self.tree , **self._expandGroup(pv)}
        else:
            self.tree = {**self.tree , **self._expandGroup(pvs)}

    def getDict(self):
        return self.tree

    def _tryCaget(self,pv):

        try:
            result = caget(pv,timeout=0.5)
        except Exception as e:
            print(str(e))
            result = 0

        return result


    def _getAllGaugePVsInGroup(self,groupPv):
        inputs = list()
        selInputFields = ["A","B","C","D","E","F","G","H","I","J","K","L"]

        for inp in selInputFields:
            try:
                input = self._tryCaget(f'{groupPv}.INP{inp}').split()[0]
                if input not in inputs:
                    inputs.append(input)
            except:
                pass

        return inputs


    def _expandGroup(self,group):

        expanded = self._getAllGaugePVsInGroup(group)
        self.level += 1
        if self.level > self.maxLevel:
            self.maxLevel = self.level

        structureDict = dict()
        structureDict[group] = list()

        for gauge in expanded:
            if 'GIMG' in gauge:
                structureDict[group].append(self._expandGroup(gauge))
            else:
                structureDict[group].append(gauge)
        self.level -= 1
        return structureDict