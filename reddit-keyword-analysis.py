import praw
import pandas as pd
import settings
import tools

#Set to True to delete datafile and generate new one
REFRESH_DATA = True

# Load or generate data

submissions, comments = tools.load_data(
        settings.SUBREDDIT, settings.NUMBER_OF_SUBMISSIONS, REFRESH_DATA)

#Make a count of the terms
for term in settings.TERMS:
        #Submissions
        sub_term_check = submissions.title.str.contains(f'{term}',case=False)
        submissions[f'Contains{term}'] = sub_term_check
        #Comments
        com_term_check = comments.text.str.contains(f'{term}',case=False)
        comments[f'Contains{term}'] = com_term_check

#Include a column for any term
comments['ContainsAny']= (comments.filter(regex="Contains",axis=1).any(axis=1))

# Create new dataframe with % of comments containing terms
a = comments.groupby(['subreddit']).size().to_frame('number_of_comments').reset_index()
b = comments.loc[comments.ContainsAny]
b = b.groupby(['subreddit']).size().to_frame('number_of_comments_with_terms').reset_index()
result = pd.merge(a,b, on="subreddit", how='outer')
result['percentage'] = result['number_of_comments_with_terms'] / result['number_of_comments']
print(result)