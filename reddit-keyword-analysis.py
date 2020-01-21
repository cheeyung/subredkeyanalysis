import praw
import pandas as pd
import settings
import tools
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

#Set to True to delete datafile and generate new one
REFRESH_DATA = False

# Load or generate data
submissions, comments = tools.load_data(
        settings.SUBREDDIT, settings.NUMBER_OF_SUBMISSIONS, REFRESH_DATA)

# Check for presence of each term
submissions, comments = tools.term_check(submissions, comments, settings.TERMS)

## Run analysis
# comments_analysis = tools.term_analysis(comments, 'comments')
# submissions_analysis = tools.term_analysis(submissions, 'submissions')
# print(submissions_analysis)
# print(comments_analysis)

df = comments.loc[comments.ContainsAny]
df = df[['score','createddate','subreddit']]

##Basic plot
# xthreshold = df.createddate.mean() - df.createddate.std()
# df = df[df['createddate'] > xthreshold]
# ythreshold = df.score.mean() + 10*df.score.mean()
# df = df[df['score'] < ythreshold]
# df['createddate'] = pd.to_datetime(df['createddate'], unit='s')
# sns.set(style='darkgrid')
# g = sns.relplot(x="createddate", y="score", hue="subreddit", data=df)
# g.set(
#         xlim=(df['createddate'].min(), df['createddate'].max()),
#         ylim=(0,df['score'].max()),
# )
# g.set_xticklabels(rotation=45)

df['createddate'] = pd.to_datetime(df['createddate'], unit='s')
df['createddate'] = df['createddate'].dt.strftime("%b %Y")
z = df.groupby(['subreddit','createddate']).size().to_frame('count').reset_index()

z = z.set_index(['subreddit','createddate']).unstack(fill_value=0).stack().reset_index()

#multi = [(x,y) for x in z['subreddit'].unique() for y in z['createddate'].unique()]
#z =z.set_index(['subreddit','createddate']).reindex(multi).fillna(0).reset_index()

print(z.sort_values(by=['subreddit']).head(10))

pal = sns.cubehelix_palette(10, rot=-.2, light=.5)
g = sns.FacetGrid(z, row="subreddit", hue="subreddit", 
                aspect=15, height=0.6, palette=pal)

g.map(sns.lineplot, 'createddate', "count", data=z)

def label(x, color, label):
    ax = plt.gca()
    ax.text(0, .2, label, fontweight="bold", color=color,
            ha="left", va="center", transform=ax.transAxes)

g.map(label, "count")

g.fig.subplots_adjust(hspace=-.05)

g.set_titles("")
g.set(yticks=[])
g.despine(left=True)
g.set_xticklabels(rotation=45)

plt.show()