import pandas as pd

class TableAgeEfficiency:
   __table = None

   @staticmethod 
   def get_table():
      """ Static access method. """
      if TableAgeEfficiency.__table is None:
         TableAgeEfficiency()
      return TableAgeEfficiency.__table

   def __init__(self):
      """ Virtually private constructor. """
      if TableAgeEfficiency.__table != None:
         raise Exception("This class is a singleton!")
      else:
         TableAgeEfficiency.__table = pd.read_csv("EER-BY-YEAR.csv")