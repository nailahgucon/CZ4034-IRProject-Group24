from datetime import datetime


class records():
    docs = None
    displayDocs = []

    @classmethod
    def store(cls, docs):
      
      cls.displayDocs = docs
      cls.docs = docs
    
    def filterByRating(self, rating):
      result = []
      for i in self.docs:
        if float(i["Rating"][0]) == float(rating):
          result.append(i)

      self.displayDocs = result
      return self.displayDocs
    
    def filterByDate(self, start_date, end_date):
      result = []
      for i in self.docs:
        date = datetime.strptime(i["Date"], '%B %d, %Y')
        
        if date >= start_date and date <= end_date:
          result.append(i)
      
      self.displayDocs = result
      return self.displayDocs
    
    def filterByDateAndRating(self,start_date, end_date,rating):
      result = []
      for i in self.docs:
        date = datetime.strptime(i["Date"][0], '%B %d, %Y')
        if date >= start_date and date <= end_date and i["Rating"] == rating:
          result.append(i)
      self.displayDocs.append(i)
      return self.displayDocs
    
    def getAllRecords(self):
      return self.docs
    
    def getDisplayRecords(self):
      return self.displayDocs