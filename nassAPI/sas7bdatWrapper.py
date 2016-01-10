import codecs

from sas7bdat import SAS7BDAT

class SAS7BDATUtil(SAS7BDAT):
    """
    SAS7BDAT with extra functionality
    
    Currently provides column name decoding and other utility functions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        #Decode column names
        self.column_names_decoded = [codecs.decode(db.encoding, db.encoding_errors) for str in self.column_names]
        #Sort by col_id just to be sure
        def k(a):
            return a.col_id
        self.column_names_decoded.sort(key=k)

    def colToIdx(self, colName):
        return self.column_names_decoded.index(colName)
        
    def idxToCol(self, idx):
        return self.column_names_decoded[idx]
    
    def rowToKVs(self, row):
        return dict(zip(self.column_names_decoded, row))
        
        