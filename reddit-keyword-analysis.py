import praw
import pandas as pd
import settings
import tools

#Set to True to delete datafile and generate new one
REFRESH_DATA = True

# Load or generate data

data = tools.load_data(
        settings.SUBREDDIT, settings.NUMBER_OF_SUBMISSIONS, REFRESH_DATA)
submissions = data[0]
comments = data[1]

#Make a count of the terms

for term in settings.TERMS:
        #Submissions
        sub_term_check = submissions.title.str.contains(f'{term}',case=False)
        submissions[f'Contains{term}'] = sub_term_check
        #Comments
        com_term_check = comments.text.str.contains(f'{term}',case=False)
        comments[f'Contains{term}'] = com_term_check

print(submissions)
print(comments)

count = {'submissions':{}, 'comments':{}}
com_count = {}

for term in settings.TERMS:
        count['submissions'][f'{term}'] = submissions[f'Contains{term}'].sum()
        count['comments'][f'{term}'] = comments[f'Contains{term}'].sum()

print(count)