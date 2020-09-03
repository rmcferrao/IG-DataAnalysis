
import re
import dateutil.parser


def numberWithCommasToInt(numberStr):
  return int(numberStr.replace(",", ""))

def dateISO8601ToReadable(datestring):
  return dateutil.parser.parse(datestring)

def numberToWeekDay(number):
  weekDays = ("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")
  return weekDays[number]

def quantifierToAbsolute(nValue, quantifier):
  if quantifier == 'k':
    return str(int(float(nValue) * 1000))

  elif quantifier == 'm':
    return str(int(float(nValue) * 1000000))

  else:
    return nValue

def getLikesFromMetaDescription(description):
  pattern = r'^([0-9\.]*)([m,k])?\sLikes'
  regex = re.search(pattern, description)
  nLikes = regex.group(1)
  quantifier = regex.group(2)

  return int(quantifierToAbsolute(nLikes, quantifier))

def getCommentsFromMetaDescription(description):
  pattern = r'\s([0-9\.]*)([m,k])?\sComments'
  regex = re.search(pattern, description)
  if not regex:
    return None

  nComments = regex.group(1)
  quantifier = regex.group(2)

  return int(quantifierToAbsolute(nComments, quantifier))

def getTaggedPeopleFromPhotoAlt(altPhoto):
  pattern = r'@(\S+)(?:(?:,|\.)\s|(?:,\sand))'
  taggedPeople = re.findall(pattern, altPhoto)

  if not taggedPeople:
    return [None]

  return taggedPeople

def getImageMayContainFromPhotoAlt(altPhoto):
  try:
    mayContain = altPhoto.split('Image may contain:')[1][:-1]
    pattern = r'(?:,|(?:\sand\s))' 
    contains = re.split(pattern, mayContain)
    containsStrip = [contain.strip() for contain in contains]

    return containsStrip

  except:
    return [None]

def flatList(list):
  l = [item for sublist in list for item in sublist]
  return l