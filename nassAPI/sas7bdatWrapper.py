import codecs

from sas7bdat import SAS7BDAT

class SAS7BDATUtil(SAS7BDAT):
    """
    SAS7BDAT with extra functionality
    
    Currently provides column name decoding and other utility functions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #Sort columns first to be sure of right order
        def k(a):
            return a.col_id
        self.tmpColumns = self.columns[:]
        self.tmpColumns.sort(key=k)
        
        #Decode column names
        self.column_names_decoded = [codecs.decode(col.name, self.encoding, self.encoding_errors) for col in self.tmpColumns]
        del self.tmpColumns

    def colToIdx(self, colName):
        return self.column_names_decoded.index(colName)
        
    def idxToCol(self, idx):
        return self.column_names_decoded[idx]
    
    def rowToKVs(self, row):
        return dict(zip(self.column_names_decoded, row))
        
        