from assets import Asset, Proposal
from utility import Assumptions
from pyllist import dllist, dllistnode

class Site:
    
    #constructor + instance variables
    def __init__(self, id):
        self.id = id
        self.portfolio = None
        self.proposal_list = dllist()
        self.assumptions = Assumptions.Assumptions()
        
    def dump(self):
        print("ID: " + str(self.id))
        print("Total Assets:" + str(self.proposal_list.size))
        for x in self.proposal_list.iternodes():
            if (x != None):
                x.value.dump()
        print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
        print()
        
    def add_proposal(self, proposal):
        if (not isinstance(proposal, Proposal.Proposal)):
            raise TypeError("Cannot add a non Proposal type to site proposal_list")
        self.proposal_list.appendright(proposal)
        proposal.site = self