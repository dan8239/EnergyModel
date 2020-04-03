from Asset import *
from Proposal import *
from Assumptions import *
from pyllist import dllist, dllistnode

class Site:

    #class variables
    compare_asset = Asset()
    
    #constructor + instance variables
    def __init__(self, id, assumptions = None):
        self.id = id
        self.proposal_list = dllist()
        self.proposal_id_generator = 0
        self.assumptions = Assumptions()
        
    def print_all(self):
        print("ID: " + str(self.id))
        print("Total Assets:" + str(self.proposal_list.size))
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.dump()
        print()
        
    def add_proposal(self, proposal):
        if (not isinstance(proposal, Proposal)):
            raise TypeError("Cannot add a non Proposal type to site proposal_list")
        self.proposal_list.appendright(proposal)
        proposal.site = self
        proposal.prop_id = self.proposal_id_generator
        self.proposal_id_generator += 1