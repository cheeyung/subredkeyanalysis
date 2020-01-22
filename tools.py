import sys
import praw
import pandas as pd

def progressbar(current, total):
    bar_length = 60
    filled_length = int(bar_length*current/total)

    percent = round(current/total*100,1)

    bar = (filled_length * "=") + (bar_length-filled_length) * "-"
    progressbar_str = f'[{bar}] {percent}%'
    sys.stdout.write(f'Scraping comments.. {progressbar_str}\r')
    sys.stdout.flush()

def load_data(subreddits, number_of_submissions, refresh_data, get_comments=True, submission_datafile="submission_data.csv",
    comments_datafile="comments_data.csv"):
    """
    Scrapes the submission titles and comments from a list of subreddits if refresh_data is True
    Loads from existing CSV if refresh_data is false

    Loads comments only if get_comments=True

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
    subreddit_number = 0
    total_number_of_submissions = number_of_submissions * len(subreddits)

    if refresh_data == True:
        #Extract the submissions
        try:
            os.remove(submission_datafile)
            os.remove(comments_datafile)
        except:
            pass
        for subreddit in subreddits:
            subreddit_number += 1
            print(f'[{subreddit_number}/{len(subreddits)}] Starting scrape of r/{subreddit}')
            try:
                new_submissions = reddit.subreddit(subreddit).hot(limit=number_of_submissions)
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
            except:
                print(f'r/{subreddit} inaccessible')
            submissions = pd.DataFrame(submissions_list, columns=['title','score',
                'comments','selftext','createddate', 'link_id', 'subreddit'])
        #Save to file
        submissions.to_csv(submission_datafile)
        if get_comments == True:
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
            comments.to_csv(comments_datafile)
        else:
            comments = ['']

    #Load data from existing CSVs if REFRESH_DATA = False
    else:
        try:
            submissions = pd.read_csv(submission_datafile,index_col=0)
            if get_comments == True:
                comments = pd.read_csv(comments_datafile,index_col=0)
            else:
                comments = ['']
        except:
            print('No data to load - set REFRESH_DATA to True')
            exit()

    return submissions, comments


def term_check(submissions_df, comments_df, terms):
    '''
    Checks for the presence of each term in the submissions and comments dataframe.

    Returns the original dataframe with appended columns with True/False for each term. 
    Also appends a column that is True if any of the terms is present
    '''
    #Make a count of the terms
    for term in terms:
            #Submissions
            sub_term_check = submissions_df.title.str.contains(f'{term}',case=False)
            submissions_df[f'Contains{term}'] = sub_term_check
            #Comments
            com_term_check = comments_df.text.str.contains(f'{term}',case=False)
            comments_df[f'Contains{term}'] = com_term_check

    #Include a column for any term
    for df in [submissions_df, comments_df]:
        df['ContainsAny']= (df.filter(regex="Contains",axis=1).any(axis=1))

    return submissions_df, comments_df

def term_analysis(df, scope):
    '''
    Runs terms analysis from output dataframes from termcheck().

    Work in progress
    '''

    # Create new dataframe with % of comments containing terms
    a = df.groupby(['subreddit']).size().to_frame(f'number_of_{scope}').reset_index()
    b = df.loc[df.ContainsAny]
    b = b.groupby(['subreddit']).size().to_frame(f'number_of_{scope}_with_terms').reset_index()
    result = pd.merge(a,b, on="subreddit", how='outer')
    result['percentage'] = result[f'number_of_{scope}_with_terms'] / result[f'number_of_{scope}'] * 100

    #Get mean scores
    c = df.groupby(['subreddit']).score.mean().to_frame(f'mean score of all {scope}').reset_index() 
    d = df.loc[df.ContainsAny].groupby(['subreddit']).score.mean().to_frame(f'mean score of all {scope} with terms').reset_index()
    e = df.loc[df.ContainsAny==False].groupby(['subreddit']).score.mean().to_frame(f'mean score of all other {scope}').reset_index()

    for i in [c,d,e]: #merge into results dataframe
        result = pd.merge(result, i, on="subreddit", how="outer")
    
    result["score_positivity"] = result[f'mean score of all {scope} with terms'] / result[f'mean score of all other {scope}']

    return result