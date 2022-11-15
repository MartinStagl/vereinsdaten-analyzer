import pandas as pd
from dtale.app import build_app
from dtale.views import startup
from flask import redirect
import sqlite3

from flask import request
from flask_bootstrap import Bootstrap
from flask import Flask,render_template,request, jsonify, url_for, url_for, redirect

navigation=[] 

query_teams_end_of_season=""" 
select name,league,season,points
from (
select 
sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
    ) points,
	sum(
	CASE WHEN m.home_team_id==t.id THEN homeresult WHEN  m.away_team_id==t.id THEN awayresult ELSE 0 END
	)  scored,
    sum(
	CASE WHEN m.home_team_id==t.id THEN awayresult WHEN  m.away_team_id==t.id THEN homeresult  ELSE 0 END
	)  conceded,
	 *
from teams t join  (
select substr(result,0,instr(result, ':')) as homeresult,
		substr(result,instr(result, ':') + 1) as awayresult,
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
		,* from matches) m on (t.id=m.away_team_id or t.id=m.home_team_id)
		group by season,league,t.name 
order by season,league,points desc) m 
"""


query_spiele_spieler = """
Select * from 
(
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
		where current_round != 0 ) m  
		join matches_players mp on m.id=mp.match_id 
		join players p on mp.player_id=p.id
"""



query_spiele_statistics = """
Select p.name, m.league, season, t.name as "Team",  count(m.url) as "number_of_matches",
	sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	) points,
	sum(
	CASE WHEN homeresult==awayresult THEN 0 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 1 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 1 ELSE 0 END
	)  wins,
	sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 0 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 0 ELSE 0 END
	)  draws,
	sum(
	CASE WHEN homeresult==awayresult THEN 0 WHEN homeresult<awayresult and m.home_team_id==t.id THEN 1 WHEN homeresult>awayresult and m.away_team_id==t.id THEN 1 ELSE 0 END
	)  loses,
	sum(
	CASE WHEN m.home_team_id==t.id THEN homeresult WHEN  m.away_team_id==t.id THEN awayresult ELSE 0 END
	)  scored,
	sum(
	CASE WHEN m.home_team_id==t.id THEN awayresult WHEN  m.away_team_id==t.id THEN homeresult  ELSE 0 END
	)  conceded,
	sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	)/count(m.url) "points/game",sum(mp.goals) as "goals scored",sum(mp.yellow_cards) as "yellow_card", sum(mp.red_cards) as "red_card"
from  (
	select substr(result,0,instr(result, ':')) as homeresult,
	substr(result,instr(result, ':') + 1) as awayresult,
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
	,* from matches) m 
	join matches_players mp on m.id=mp.match_id 
	join teams t on (t.id=mp.team_id)
	join players p on mp.player_id=p.id
	--- join (select DISTINCT match_id,team_id,GROUP_CONCAT(minute,';') as "first_substitution_min", count(type) as "num_subs" 
	---      from (select DISTINCT match_id,team_id,minute,type from matches_activity) where type = 'substitution' group by match_id,team_id) a  on m.id=a.match_id

group by season,m.league, t.name,p.name
order by p.name
"""

query_goals_per_min=("""
select  *--count(*) as "Goals_per_min_conceeded"
from  (select DISTINCT match_id,minute,type,team_id,text from matches_activity) a 
join matches m on m.id=a.match_id
join  teams t on (t.id=m.away_team_id or t.id=m.home_team_id)
where type="goal" 
		and a.team_id<>t.id 
        type="goal"
group by m.league,t.name, minute
order by minute,name
""")

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
order by season,league,current_round asc,running_points desc) m 
"""

def query_database(query,database='verbands.db'):
    '''
    Load data from database
    :param query: Specifies in an SQL Select statement which data to load
    :param database: Path to database
    :return: Pandas Dataframe of resultset
    '''
    cnx = sqlite3.connect(database)
    df = pd.read_sql_query(query, cnx)
    cnx.commit()
    cnx.close()
    cols=pd.Series(df.columns)
    for dup in cols[cols.duplicated()].unique(): 
        cols[cols[cols == dup].index.values.tolist()] = [dup + '.' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
    # rename the columns with the cols list.
    df.columns=cols
    return df


if __name__ == '__main__':
    app = build_app(reaper_on=False,additional_templates='templates')
    Bootstrap(app)
	
    @app.errorhandler(404)
    def not_found_error(error):
       return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('500.html'), 500

    @app.route("/load-data")
    def create_df():
        dataset = request.args.get('data', default = "query_teams_end_of_season", type = str)
        df=pd.DataFrame()
        if dataset=="query_teams_end_of_season":
            df=query_database(query_teams_end_of_season,database="verbands.db")
        elif dataset=="query_spiele_spieler":
            df=query_database(query_spiele_spieler,database="verbands.db")
        elif dataset=="query_spiele_statistics":
            df=query_database(query_spiele_statistics,database="verbands.db")
        elif dataset=="query_goals_per_min":
            df=query_database(query_goals_per_min,database="verbands.db")
        elif dataset=="query_points_per_league_season_round_team":
            df=query_database(query_points_per_league_season_round_team,database="verbands.db")
        df["rank"]=df.groupby(["season","league"])["points"].rank(method="dense", ascending=False)
        instance = startup(data=df, ignore_duplicate=True)
        return redirect(f"/dtale/main/{instance._data_id}", code=302)

    @app.route("/")
    def hello_world():
       return render_template('index.html', navigation=navigation)

    app.run(host="127.0.0.1", port=8000)