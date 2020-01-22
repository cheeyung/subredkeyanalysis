import praw
import pandas as pd
import settings
import tools
import matplotlib.pyplot as plt
import seaborn as sns

#Set to True to delete datafile and generate new one
REFRESH_DATA = True

# Load or generate data
submissions, comments = tools.load_data(
        settings.SUBREDDIT, settings.NUMBER_OF_SUBMISSIONS, REFRESH_DATA)

# Check for presence of each term
submissions, comments = tools.term_check(submissions, comments, settings.TERMS)

## Run analysis
comments_analysis = tools.term_analysis(comments, 'comments')
submissions_analysis = tools.term_analysis(submissions, 'submissions')
submissions_analysis.to_csv('submissions_analysis.csv')
comments_analysis.to_csv('comments_analysis.csv')

# Begin plotting
df = comments_analysis
df_false = df.loc[df.percentage.isna()]
df_false.to_csv('No terms.csv')
df = df.dropna()

g = sns.scatterplot(x='percentage', y='score_positivity', hue='subreddit', data=df)


x_min_threshold = 0
x_max_threshold = df['percentage'].mean() + 3* df['percentage'].std()
y_min_threshold = df['score_positivity'].mean() - 1 * df['score_positivity'].std()
y_max_threshold = df['score_positivity'].mean() + 2 * df['score_positivity'].std()

g.set(
      xlim=(x_min_threshold, x_max_threshold),
      ylim=(y_min_threshold, y_max_threshold),
      xlabel= f'% of comments with sustainability terms in it',
      ylabel = f'Score positivity',
)

plt.gca().grid(True)

plt.show()
