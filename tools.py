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

def load_data(subreddit, number_of_submissions, refresh_data, submission_datafile="submission_data.csv",
    comments_datafile="comments_data.csv"):

    #Initialisation 
    reddit = praw.Reddit('reddit')
    submissions_list = []
    comments_list = []
    sub_no = 0

    if refresh_data == True:
        #Extract the submissions
        try:
            os.remove(submission_datafile)
            os.remove(comments_datafile)
        except:
            pass
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
        for index, row in submissions.iterrows():
            progressbar(index, number_of_submissions)
            link_id_str = str(row['link_id'])
            submission_child = reddit.submission(id=link_id_str)
            submission_child.comments.replace_more(limit=None)
            for comment in submission_child.comments.list():
                comments_list.append([
                    comment.body,
                    comment.score,
                    comment.created,
                    subreddit,
                    ])
        comments = pd.DataFrame(comments_list, columns=['text','score','createddate','subreddit'])
        #Save to file
        submissions.to_csv(submission_datafile)
        comments.to_csv(comments_datafile)
    else:
        submissions = pd.read_csv(submission_datafile,index_col=0)
        comments = pd.read_csv(comments_datafile,index_col=0)
    return submissions, comments