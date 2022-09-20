import plotly.express as px

from data_provider import *


query_points_per_league_season_round_team="""
select scored-conceded as difference, *
from (
select 
sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	) OVER (
		PARTITION BY season,league,name
        ORDER BY current_round
    ) running_points,
	sum(
	CASE WHEN m.home_team_id==t.id THEN homeresult WHEN  m.away_team_id==t.id THEN awayresult ELSE 0 END
	) OVER (
		PARTITION BY season,league,name
        ORDER BY current_round
    ) scored,
    sum(
	CASE WHEN m.home_team_id==t.id THEN awayresult WHEN  m.away_team_id==t.id THEN homeresult  ELSE 0 END
	) OVER (
		PARTITION BY season,league,name
        ORDER BY current_round
    ) conceded,
	 *
from teams t join  (
select substr(result,0,instr(result, ':')) as homeresult,
		substr(result,instr(result, ':') + 1) as awayresult, cast(substr(round,0,instr(round, '.')) as INT) as current_round,
		CASE 
		   WHEN replace(date,'-','') between '20110701' and '20120701' THEN '2011/12'
		   WHEN replace(date,'-','') between '20120701' and '20130701' THEN '2012/13'
		   WHEN replace(date,'-','') between '20130701' and '20140701' THEN '2013/14'
		   WHEN replace(date,'-','') between '20140701' and '20150701' THEN '2014/15'
		   WHEN replace(date,'-','') between '20150701' and '20160701' THEN '2015/16'
		   WHEN replace(date,'-','') between '20160701' and '20170701' THEN '2016/17'
		   WHEN replace(date,'-','') between '20170701' and '20180701' THEN '2017/18'
		   WHEN replace(date,'-','') between '20180701' and '20190701' THEN '2018/19'
		   WHEN replace(date,'-','') between '20190701' and '20200701' THEN '2019/20'
		   WHEN replace(date,'-','') between '20200701' and '20210701' THEN '2020/21'
		   WHEN replace(date,'-','') between '20210701' and '20220701' THEN '2021/22'
		   WHEN replace(date,'-','') between '20220701' and '20230701' THEN '2022/23'
		   ELSE 'undefined'
		END as season
		,* from matches
		where current_round != 0 ) m on (t.id=m.away_team_id or t.id=m.home_team_id)
order by season,league,current_round asc,running_points desc) m where season='2021/22'
"""

df=query_database(query_points_per_league_season_round_team)
print(df.head())
fig=px.scatter(df, x="difference", y="running_points", animation_frame="current_round", animation_group="name",
           color="league", hover_name="name",
           log_x=True, size_max=55, range_x=[0,200], range_y=[0,120])

fig.write_html("./plots/interactive_plotly.html")