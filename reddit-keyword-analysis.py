import praw
import pandas as pd
import settings
import tools

#Set to True to delete datafile and generate new one
REFRESH_DATA = False

# Load or generate data
submissions, comments = tools.load_data(
        settings.SUBREDDIT, settings.NUMBER_OF_SUBMISSIONS, REFRESH_DATA)

# Check for presence of each term
submissions, comments = tools.term_check(submissions, comments, settings.TERMS)

# Run analysis
comments_analysis = tools.term_analysis(comments, 'comments')
submissions_analysis = tools.term_analysis(submissions, 'submissions')
print(submissions_analysis)
print(comments_analysis)
