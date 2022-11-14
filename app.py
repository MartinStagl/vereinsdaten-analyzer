import pandas as pd
from dtale.app import build_app
from dtale.views import startup
from flask import redirect
import sqlite3


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
    app = build_app(reaper_on=False)


    @app.route("/create-df")
    def create_df():
        df=query_database(query_teams_end_of_season,database="verbands.db")
        df["rank"]=df.groupby(["season","league"])["points"].rank(method="dense", ascending=False)
        instance = startup(data=df, ignore_duplicate=True)
        return redirect(f"/dtale/main/{instance._data_id}", code=302)


    @app.route("/")
    def hello_world():
        return 'Hi there, load data using <a href="/create-df">create-df</a>'


    app.run(host="127.0.0.1", port=8000)