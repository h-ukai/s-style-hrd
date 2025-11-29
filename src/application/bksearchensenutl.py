from models.bksearchensen import bksearchensen
from models.bksearcheki import bksearcheki

class bksearchensenutl(object):
    ensen = None

    def newensen(self,ref_bksearchdata , ensenmei ,tdufknmi = None, thHnU = None, thMU = None):
        if thHnU:
            thHnU = float(thHnU)
        else:
            thHnU = None
        if thMU:
            thMU = float(thMU)
        else:
            thMU = None
        self.ensen = bksearchensen(ref_bksearchdata=ref_bksearchdata , tdufknmi=tdufknmi, ensenmei=ensenmei , thHnU = thHnU, thMU = thMU,srotkey = ref_bksearchdata.getNextlinelistNum())
        self.ensen.put()

    def delete(self):
        for eki in self.ensen.eki:
            eki.delete()
        self.ensen.delete()
        
    def addeki(self,ekistr):
        for eki in self.ensen.eki:
            if eki.ekimei == ekistr:
                return None
        return bksearcheki(ref_ensen = self.ensen,ekimei = ekistr).put()
    
    def deleki(self,ekistr):
        for eki in self.ensen.eki:
            if eki.ekimei == ekistr:
                eki.delete()
                break