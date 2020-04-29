from ecm import Ecm
from pyllist import dllist, dllistnode

class EcmManager():
    """description of class"""
    def __init__(self):
        self.__ecm_lists = dllist()

    def add_ecm_list(self, ecm_description):
        self.__ecm_lists.appendright(EcmList(ecm_description))

    def get_ecm_list(self, ecm_description):
        ecm_list = None
        for x in self.__ecm_lists.iternodes():
            if (x.value.ecm_description == ecm_description):
                ecm_list = x.value
                return ecm_list
        if (ecm_list == None):
            raise TypeError("No Ecm List Found for Description " + str(ecm_description))

    def add_ecm(self, ecm_description, ecm):
        if (not isinstance(ecm, Ecm.Ecm)):
            raise TypeError("Cannot Attach non-ECM type to ECM List")
        ecm_list = self.get_ecm_list(ecm_description)
        ecm_list.add_ecm(ecm)

class EcmList():
    def __init__(self, ecm_description):
        self.ecm_description = ecm_description
        self.__ecm_list = dllist()

    def add_ecm(self, ecm):
        self.__ecm_list.appendright(ecm)

    def apply_ecms(self, asset):
        for x in self.__ecm_list.iternodes():
            if (x != None):
                x.value.apply_ecm(asset)
