# -*- coding: utf-8 -*-


import unittest
from pprint import pprint

from hoboreader import HoboReader

class TestPendant(unittest.TestCase):
    
    def test_read_csv(self):
        
        fp='sample_hobo_pendant_data.csv'
        h=HoboReader(fp)
        
        #print(h.header_row)
        #print(h.header_list)
        
        
    def test_get_dataframe(self):
        
        fp='sample_hobo_pendant_data.csv'
        h=HoboReader(fp)
        df=h.get_dataframe()
        
        #print(df.head(1))
        
        
    def test_get_rdf(self):
        
        fp='sample_hobo_pendant_data.csv'
        h=HoboReader(fp)
        g=h.get_rdf()
        
        #print(g)
        
        
class TestU12(unittest.TestCase):
    
    def test_read_csv(self):
        
        fp='sample_hobo_u12_data.csv'
        h=HoboReader(fp)
        
        #print(h.header_row)
        #print(h.header_list)
        
        
    def test_get_dataframe(self):
        
        fp='sample_hobo_u12_data.csv'
        h=HoboReader(fp)
        df=h.get_dataframe()
        
        #print(df.head(1))
        
        
    def test_get_rdf(self):
        
        fp='sample_hobo_u12_data.csv'
        h=HoboReader(fp)
        g=h.get_rdf()
        
        #print(g)
        #print(len(g))
        
        
if __name__=='__main__':
    
    o=unittest.main(TestPendant())  
    o=unittest.main(TestU12())
    