from pathlib import Path
from pgmpy.readwrite import BIFReader
import pyGMs

def convertBifToUai(bifPath,uaiPath=None):
    