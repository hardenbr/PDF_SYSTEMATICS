from optparse  import OptionParser
import ROOT as rt
import array, os
import random, math

parser.add_option("-r", "--raw", dest="raw",
                  help="vecbos file containing PDF information",
                  default="default.root",
                  action="store",type="string")

parser.add_option("-s","--sel",dest="sel",
                  help="hgg selection file corresponding to said vecbos file",
                  action="store",type="string")

class pdf_set:
    def __init__(self, name, nvecs):
        self.name = name

        #constants
        self.nvecs = nvecs
        self.npairs = (nvecs - 1) / 2

        #eigenvector information
        self.zero = [] #holds the nominal value of the lumi function
        self.vec_a = [] #first value in the eigenvector pair
        self.vec_b = [] #seoncd value in the eigenvector pair

        #build the internal structore
        for ii in xrange(self.npairs):
            self.vec_a.append([])
            self.vec_b.append([])
        
    def add_event_pdfs(self, pdfs):

        if self.nvecs != len(pdfs):
            print "\t\tNUMBER OF EIGENVECTORS DOES NOT MATCH!"
            exit(1)
            
        #append the zero
        self.zero.append(pdfs[0])

        #append the rest
        for ii in xrange(npairs):
            self.vec_a[ii].append(pdfs[2*ii + 1])
            self.vec_b[ii].append(pdfs[2*ii + 2])
            
    def get_sum_nominal(self):
        return sum(self.zero)

    def get_sum_veca(self,index):
        return sum(self.vec_a[ii])

    def get_sum_vecb(self,index):
        return sum(self.vec_b[ii])

    
        
