import praw
import pandas as pd
import os
import settings
from progressbar import progressbar


#Set to True to delete datafile and generate new one
REFRESH_DATA = False

#Initialisation 
reddit = praw.Reddit('reddit')
submissions_list = []
comments_list = []
sub_no = 0

# Load or generate data
if REFRESH_DATA == True:
        #Extract the submissions
        try:
                os.remove(settings.SUBMISSION_DATAFILE)
                os.remove(settings.COMMENTS_DATAFILE)
        except:
                pass
        new_submissions = reddit.subreddit(settings.SUBREDDIT).new(limit=settings.NUMBER_OF_SUBMISSIONS)
        for submission in new_submissions:
                submissions_list.append([
                        submission.title, 
                        submission.score, 
                        submission.num_comments, 
                        submission.selftext, 
                        submission.created,
                        submission.id,
                        settings.SUBREDDIT,
                        ])
        submissions = pd.DataFrame(submissions_list, columns=['title','score',
        'comments','selftext','createddate', 'link_id', 'subreddit'])
        #extract the comments
        for index, row in submissions.iterrows():
                progressbar(index, settings.NUMBER_OF_SUBMISSIONS)
                link_id_str = str(row['link_id'])
                submission_child = reddit.submission(id=link_id_str)
                submission_child.comments.replace_more(limit=None)
                for comment in submission_child.comments.list():
                        comments_list.append([
                                comment.body,
                                comment.score,
                                comment.created,
                                settings.SUBREDDIT,
                        ])
        comments = pd.DataFrame(comments_list, columns=['text','score','createddate','subreddit'])
        #Save to file
        submissions.to_csv(settings.SUBMISSION_DATAFILE)
        comments.to_csv(settings.COMMENTS_DATAFILE)
else:
        submissions = pd.read_csv(settings.SUBMISSION_DATAFILE,index_col=0)
        comments = pd.read_csv(settings.COMMENTS_DATAFILE,index_col=0)

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