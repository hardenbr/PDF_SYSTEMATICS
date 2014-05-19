from optparse  import OptionParser
import ROOT as rt
import array, os
import random, math

parser = OptionParser()

parser.add_option("-r", "--raw", dest="raw",
                  help="vecbos file containing PDF information",
                  default="default.root",
                  action="store",type="string")

parser.add_option("-s","--sel",dest="sel",
                  help="hgg selection file corresponding to said vecbos file",
                  action="store",type="string")

(options, args) = parser.parse_args()

class pdf_set:
    def __init__(self, name, nvecs):
        self.name = name

        #constants
        self.nvecs = nvecs
        self.npairs = (nvecs - 1) / 2

        #eigenvector information
        self.zero = [] #holds the nominal value of the lumi function
        self.vec_a = [] #first value in the eigenvector pair
        self.vec_b = [] #second value in the eigenvector pair

        #build the internal structore
        for ii in xrange(self.npairs):
            self.vec_a.append([])
            self.vec_b.append([])
        
    def add_event_pdfs(self, pdfs):

        #if self.nvecs != len(pdfs):
        #    print "\t\tNUMBER OF EIGENVECTORS DOES NOT MATCH!"
        #    exit(1)
            
        #append the zero
        self.zero.append(pdfs[0])

        #append the rest
        for ii in xrange(self.npairs):
            self.vec_a[ii].append(pdfs[2*ii + 1])
            self.vec_b[ii].append(pdfs[2*ii + 2])
            
    def get_sum_nominal(self):
        return sum(self.zero)

    def get_sum_veca(self,index):
        return sum(self.vec_a[index])

    def get_sum_vecb(self,index):
        return sum(self.vec_b[index])

def get_acceptance_error(raw_set, sel_set):

    if raw_set.npairs != sel_set.npairs or raw_set.name != sel_set.name:
        print "\t\tSETS ARE NOT COMPARABLE!"
        exit(1)

    central_acc = (sel_set.get_sum_nominal() / raw_set.get_sum_nominal())

    wplus = []
    wminus = []

    for ii in range(raw_set.npairs):
        wa =  ((sel_set.get_sum_veca(ii) / raw_set.get_sum_veca(ii)) / central_acc)  - 1
        wb =  ((sel_set.get_sum_vecb(ii) / raw_set.get_sum_vecb(ii)) / central_acc) - 1 

        if raw_set.name == "NNPDF": #NNPDF IS HANDLED DIFFERENTLY
            if wa > 0: wplus.append(wa*wa)
            else: wminus.append(wa*wa)

            if wb > 0: wplus.append(wb*wb)
            else: wminus.append(wb*wb)
        else: ## ALL OTHER PDF SETS
            if wa > wb:
                if wa > 0: wplus.append(wa*wa)
                if wb < 0: wminus.append(wb*wb)
            elif wb >= wa:
                if wb > 0: wplus.append(wb*wb)
                if wa < 0: wminus.append(wa*wa)
                                    
    pos_error = math.sqrt(sum(wplus))
    neg_error = math.sqrt(sum(wminus))

    if raw_set.name == "NNPDF":
        pos_error /= math.sqrt(len(wplus))
        neg_error /= math.sqrt(len(wminus))

    return (central_acc, pos_error, neg_error)
    
#build the pdf sets
raw_nnpdf = pdf_set("NNPDF",101)
raw_cteq = pdf_set("CTEQ",45)
raw_mstw = pdf_set("MSTW",41)

sel_nnpdf = pdf_set("NNPDF",101)
sel_cteq = pdf_set("CTEQ",45)
sel_mstw = pdf_set("MSTW",41)


#fill the arrays for the raw vecbos files
raw_file = rt.TFile(options.raw,"READ")
raw_tree = raw_file.Get("ntp1")
raw_tree.Draw(">>iterlist","","entrylist")
raw_itlist = rt.gDirectory.Get("iterlist")
for event in xrange(raw_tree.GetEntries()):            
    #if event > 100: continue
    
    entry = raw_itlist.Next()        
    raw_tree.GetEntry(entry)

    #add the pdfs to the pdf set event by event
    raw_mstw.add_event_pdfs(raw_tree.wMRTW2008NNLO68)
    raw_cteq.add_event_pdfs(raw_tree.wCTEQ66)
    raw_nnpdf.add_event_pdfs(raw_tree.wNNPDF20100)

#fill the arrays for the selected sample
sel_file = rt.TFile(options.sel,"READ")
sel_tree = sel_file.Get("HggOutput")
sel_tree.Draw(">>sel_iterlist","","entrylist")
sel_itlist = rt.gDirectory.Get("sel_iterlist")
for event in xrange(sel_tree.GetEntries()):            
    #if event > 100: continue

    entry = sel_itlist.Next()        
    sel_tree.GetEntry(entry)

    if sel_tree.PFMR > 600 and sel_tree.PFR*sel_tree.PFR > .02 and sel_tree.iSamp==0:
        sel_mstw.add_event_pdfs(sel_tree.wMRTW2008NNLO68)
        sel_cteq.add_event_pdfs(sel_tree.wCTEQ66)
        sel_nnpdf.add_event_pdfs(sel_tree.wNNPDF20100)


(nnpdf_cen, nnpdf_pos, nnpdf_neg) = get_acceptance_error(raw_nnpdf, sel_nnpdf)
(cteq_cen, cteq_pos, cteq_neg) = get_acceptance_error(raw_cteq, sel_cteq)
(mstw_cen, mstw_pos, mstw_neg) = get_acceptance_error(raw_mstw, sel_mstw)

print "NNPDF",  (nnpdf_cen, nnpdf_pos, nnpdf_neg)
print "CTEQ", (cteq_cen, cteq_pos, cteq_neg) 
print "MSTW", (mstw_cen, mstw_pos, mstw_neg)

