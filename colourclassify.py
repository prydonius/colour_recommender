from colorclassifier import Classifier
import sys

_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}

def rgb(triplet):
  return (_HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]])

colorclassifier = Classifier()
classifiedColour = colorclassifier.getColourName(rgb(sys.argv[1]))
print classifiedColour