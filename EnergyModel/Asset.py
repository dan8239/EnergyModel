class Asset:
    def __init__(self, site = None, auid = 0, tons = 0, eer = 0, econ = False, vfd = False, stg_cmp = False):
        self.site = site
        self.auid = auid
        self.tons = tons
        self.eer = eer
        self.econ = econ
        self.vfd = vfd
        self.stg_cmp = stg_cmp
        
    def print_all(self):
        if ((self.site == None) or (self.site == 0)):
            print("SiteID: " + str(self.site))
        else:
            print("SiteID: " + str(self.site.id))
        print("AUID: " + str(self.auid))
        print("Tons: " + str(self.tons))
        print("EER: " + str(self.eer))
        print("Econ: %s" %self.econ)
        print("VFD: %s" %self.vfd)
        print("Staged Compressors: %s" %self.stg_cmp)
        print()