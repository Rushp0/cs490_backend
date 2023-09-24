import sys

genres = ['Action',
'Animation',
'Children',
'Classics',
'Comedy',
'Documentary',
'Drama',
'Family',
'Foreign',
'Games',
'Horror',
'Music',
'New',
'Sci-Fi',
'Sports',
'Travel'
]

for genre in genres:
    print("<option value=\"{}\">{}</option>".format(genre, genre))