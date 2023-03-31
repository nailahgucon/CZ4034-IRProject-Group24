class query():
    query = None
    style = None
    @classmethod
    def storeQuery(cls, input):
        cls.query = input
    
    def getQuery(self):
        return self.query
    
    def storeStyle(cls, input):
        cls.style = input
    
    def getStyle(self):
        return self.style