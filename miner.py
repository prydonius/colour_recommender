import dribbble as drib
from StringIO import StringIO
from PIL import Image
import requests
import io

# how many images we want to process
_max = 200
# what stream we want to process from, can be: debuts, everyone, popular
stream = "popular"
# open file for printing
outfile = io.open('dribbble_data', 'w', encoding='utf-8')
outfile.write(u"title, views, likes, comments, num_shots, followers\n")

# Attributes of interest:
#   image_url obviously
#   views_count
#   likes_count
#   comments_count???
#   player.shots_count
#   players.followers_count

count = 0
page = 0
for _ in range(0, _max):
  # 50 is the maximum per page
  resp = drib.shots('popular', per_page=50, page=page)
  for shot in resp["shots"]:
    # Get the image and open it
    img = requests.get(shot["image_url"])
    img = Image.open(StringIO(img.content))
    # Get other data
    title = shot["title"]
    views = str(shot["views_count"])
    likes = str(shot["likes_count"])
    comments = str(shot["comments_count"])
    num_shots = str(shot["player"]["shots_count"])
    followers = str(shot["player"]["followers_count"])
    outfile.write(title + ", " + views + ", " + likes + ", " + comments + ", " + num_shots + ", " + followers + "\n")
  count += 50
  if count >= _max:
    break
  page += 1
