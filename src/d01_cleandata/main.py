import json
from DataFilter import *
from os.path import dirname, join, abspath

FILE_PATH = dirname(abspath(__file__))
ROOT_FOLDER_PATH = dirname(dirname(FILE_PATH))
DATA_PATH = join(ROOT_FOLDER_PATH, 'data')

igUsers = ['luizaquental', 'gretathunberg', 'morganfreeman', 'neymarjr']
igUser = igUsers[3]

with open(join(DATA_PATH, igUser + '-raw.json')) as f:
  data = json.load(f)

postsData = data['post-data']

iNotFound = 0
postsInfo = {}

for posti, postData in postsData.items():
  postType = postData['og:type']
  description = postData['og:description']
  nLikes = postData['likes']

  if type(nLikes) is str:
    nLikes = numberWithCommasToInt(nLikes)

  if not nLikes:
    print('\n--------- LIKES NOT FOUND IN METADATA -----------\n')

    try:
      nLikes = getLikesFromMetaDescription(description)

    except:
      print('\n--------- LIKES NOT FOUND IN DESCRIPTION -----------\n')
      nLikes = -1
  
  if postType == 'video':
    imageMayContain = [[None]]
    taggedPeople = [[None]]

  if postData['photos-src-alt']:
    photosSrcAlt = {str(i): srcAlt["alt"] for i, srcAlt in enumerate(postData['photos-src-alt'])}
    imageMayContain = [getImageMayContainFromPhotoAlt(alt) for alt in photosSrcAlt.values()]
    taggedPeople = [getTaggedPeopleFromPhotoAlt(alt) for alt in photosSrcAlt.values()]

  nComments = getCommentsFromMetaDescription(description)
  if not nComments:
    nComments = -1

  dateTime = dateISO8601ToReadable(postData['date-time'])
  hourPost = dateTime.hour if dateTime.minute < 30 else dateTime.hour + 1
  weekdayPost = numberToWeekDay(dateTime.weekday()) #0 is monday 6 is sunday
  datePost = dateTime.date()

  postsInfo[posti] = {
    'url': data['post-links'][posti],
    'type': postType,
    'description': description,
    'likes': nLikes,
    'comments': nComments,
    'date': datePost.__str__(),
    'hour': hourPost,
    'week-day': weekdayPost,
    'tagged-people': taggedPeople,
    'image-may-contain': imageMayContain
  }

with open(join(DATA_PATH, f'{igUser}-cleanned.json'), 'w', encoding='utf8') as jsonfile:
    json.dump(postsInfo, jsonfile, indent=4, ensure_ascii=False)