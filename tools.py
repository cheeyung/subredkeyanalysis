import sys
import praw
import pandas as pd

def progressbar(current, total):
    bar_length = 60
    filled_length = int(bar_length*current/total)

    percent = round(current/total*100,1)

    bar = (filled_length * "=") + (bar_length-filled_length) * "-"
    progressbar_str = f'[{bar}] {percent}%'
    sys.stdout.write(f'Extracting.. {progressbar_str}\r')
    sys.stdout.flush()

def load_data(subreddits, number_of_submissions, refresh_data, submission_datafile="submission_data.csv",
    comments_datafile="comments_data.csv"):
    """
    Scrapes the submission titles and comments from a list of subreddits if refresh_data is True
    Loads from existing CSV if refresh_data is false

    Arguments
    subreddits = list of subreddits to be scraped
    number_of_submissions = number of submissions per subreddit to be scraped (max = 1000)

    Returns 2 DataFrames for submissions and comments
    """

    #Initialisation 
    reddit = praw.Reddit('reddit')
    submissions_list = []
    comments_list = []
    submission_number = 0
    total_number_of_submissions = number_of_submissions * len(subreddits)

    if refresh_data == True:
        #Extract the submissions
        try:
            os.remove(submission_datafile)
            os.remove(comments_datafile)
        except:
            pass
        for subreddit in subreddits:
            new_submissions = reddit.subreddit(subreddit).new(limit=number_of_submissions)
            for submission in new_submissions:
                submissions_list.append([
                    submission.title, 
                    submission.score, 
                    submission.num_comments, 
                    submission.selftext, 
                    submission.created,
                    submission.id,
                    subreddit,
                    ])
            submissions = pd.DataFrame(submissions_list, columns=['title','score',
                'comments','selftext','createddate', 'link_id', 'subreddit'])
        #extract the comments
        for row in submissions.itertuples():
            submission_number += 1
            progressbar(submission_number, total_number_of_submissions)
            link_id_str = str(row.link_id)
            submission_child = reddit.submission(id=link_id_str)
            submission_child.comments.replace_more(limit=None)
            for comment in submission_child.comments.list():
                comments_list.append([
                    comment.body,
                    comment.score,
                    comment.created,
                    row.subreddit,
                    ])
        comments = pd.DataFrame(comments_list, columns=['text','score','createddate','subreddit'])
        #Save to file
        submissions.to_csv(submission_datafile)
        comments.to_csv(comments_datafile)
    else:
        submissions = pd.read_csv(submission_datafile,index_col=0)
        comments = pd.read_csv(comments_datafile,index_col=0)
    return submissions, comments