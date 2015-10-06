import codecs

from sas7bdat import SAS7BDAT

class SAS7BDATUtil(SAS7BDAT):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.column_names_decoded = [codecs.decode(str, "ASCII") for str in self.column_names]

    def colToIdx(self, colName):
        return self.column_names_decoded.index(colName)
        
    def idxToCol(self, idx):
        return self.column_names_decoded[idx]
    
    def rowToKVs(self, row):
        return dict(zip(self.column_names_decoded, row))
        
        