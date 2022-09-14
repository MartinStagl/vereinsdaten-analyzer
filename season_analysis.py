import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

def query_database(query):
    '''
    Load data from database
    :param query: Specifies in an SQL Select statement which data to load
    :return: Pandas Dataframe of resultset
    '''
    cnx = sqlite3.connect('verbands.db')
    df = pd.read_sql_query(query, cnx)
    cnx.commit()
    cnx.close()
    return df

def print_more(query):
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
        print(query_database(query))

## GET GOAL Scorers
query_scorers=("Select position,t.name,p.name,goals,m.league,m.result,m.url from matches_players mp "
                  "join players p on mp.player_id=p.id "
                  "join teams t on mp.team_id=t.id "
                  "join matches m on (t.id=m.away_team_id or t.id=m.home_team_id) "
                  "order by goals desc")

# GET TABLE
query_table=("""
Select m.league,t.name, sum(
CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
) as points , count(*) as 'Number of Games'
from teams t join 
	(select substr(result,0,instr(result, ':')) as homeresult,
	substr(result,instr(result, ':') + 1) as awayresult,* from matches) m 
on (t.id=m.away_team_id or t.id=m.home_team_id) 
where replace(date,'-','') between '20210730' and '20220701'
group by m.league,t.name 
order by points desc""")


print_more(query_table)

# GET DIFFERENCE BETWEEN GOOD AND BAD TEAMS

query_top_teams="""
SELECT rnk, points,league,name
FROM (
    SELECT
      ROW_NUMBER() OVER (
        PARTITION BY  league
        ORDER BY sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	)  DESC
      ) AS "rnk",sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	) As "Points",* 
	from teams t join 
		(select substr(result,0,instr(result, ':')) as homeresult,
		substr(result,instr(result, ':') + 1) as awayresult,* from matches) m 
	on (t.id=m.away_team_id or t.id=m.home_team_id) 
	where replace(date,'-','') between '20210701' and '20220701'
	group by league,name 
  ) sub
WHERE
  "sub"."rnk" <= 2
ORDER BY
  league,rnk  ASC
"""

query_bad_teams="""
SELECT rnk, points,league,name
FROM (
    SELECT
      ROW_NUMBER() OVER (
        PARTITION BY  league
        ORDER BY sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	)  ASC
      ) AS "rnk",sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	) As "Points",* 
	from teams t join 
		(select substr(result,0,instr(result, ':')) as homeresult,
		substr(result,instr(result, ':') + 1) as awayresult,* from matches) m 
	on (t.id=m.away_team_id or t.id=m.home_team_id) 
	where replace(date,'-','') between '20210701' and '20220701'
	group by league,name 
  ) sub
WHERE
  "sub"."rnk" <= 2 
ORDER BY
  league,rnk  ASC
"""

print_more(query_top_teams)
# VISUALISE
# Goals Scored and Conceded Averages (Freekicks, Penalities eg.)
# X-Axis Goals Scored; Y-Axis Goals Conceded Highlight areas, points each team
query_goals_scored_conceded=""" 
 select league,name,
 sum(
	CASE WHEN m.home_team_id==t.id THEN homeresult WHEN  m.away_team_id==t.id THEN awayresult ELSE 0 END
	) as scored,
 sum(
	CASE WHEN m.home_team_id==t.id THEN awayresult WHEN  m.away_team_id==t.id THEN homeresult  ELSE 0 END
	) as conceded
from teams t join 
		(select substr(result,0,instr(result, ':')) as homeresult,
		substr(result,instr(result, ':') + 1) as awayresult,* from matches) m 
	on (t.id=m.away_team_id or t.id=m.home_team_id) 
where replace(date,'-','') between '20210701' and '20220701'
group by league,name """

df=query_database(query_goals_scored_conceded)
print(df.head(5))

colormap=dict([(value,key) for key,value in enumerate(set(df["league"]))])
colors=[list(mcolors.CSS4_COLORS.values())[colormap[league]] for league in df["league"]]

fig, ax = plt.subplots()
ax.scatter(df["conceded"],df["scored"],
            c=colors)

print(df.size)
for i in range(df.shape[0]):
    if i%3==0:
        ax.annotate(df.loc[i,"name"], (df.loc[i,"conceded"],df.loc[i,"scored"]))

leg = plt.legend(df["league"], fontsize=18)
for i, j in enumerate(leg.legendHandles):
    j.set_color(list(mcolors.CSS4_COLORS.values())[i])

plt.ylabel("Y-Axis Goals Scored")
plt.xlabel("X-Axis Goals Conceded")
plt.tight_layout()
plt.savefig('goals_vs_conceded.png', dpi = 300)
#plt.show()



query_goals_scored_conceded_by_type="""  """


# Fairplay
# X-Axis points Y-Axis number of cards
query_cards_by_points="""  """

# Fitness
query_goals_scored_conceded_by_15_min="""  """

# Demographic Profiles (Age, Previous Clubs, Nationality)
query_points_vs_team_age="""  """
query_points_vs_foreign="""  """

# Teams Sizes
query_points_vs_team_size="""  """

# CHECK IF DIFFERENCE IS SIGNIFICANT
# ANOVA

# PROPOSE A TABLE BASE ON FINDINGS