from data_provider import *
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


#print_more(query_table)

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

#print_more(query_top_teams)
# VISUALISE
# Goals Scored and Conceded Averages (Freekicks, Penalities eg.)
# X-Axis Goals Scored; Y-Axis Goals Conceded Highlight areas, points each team
query_goals_scored_conceded=""" 
  select league,name,season_number,
 sum(
	CASE WHEN m.home_team_id==t.id THEN homeresult WHEN  m.away_team_id==t.id THEN awayresult ELSE 0 END
	) as scored,
 sum(
	CASE WHEN m.home_team_id==t.id THEN awayresult WHEN  m.away_team_id==t.id THEN homeresult  ELSE 0 END
	) as conceded,
season
from teams t join 
		(select substr(result,0,instr(result, ':')) as homeresult,
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
		END as season,
		CASE 
		   WHEN replace(date,'-','') between '20110701' and '20120701' THEN '1'
		   WHEN replace(date,'-','') between '20120701' and '20130701' THEN '2'
		   WHEN replace(date,'-','') between '20130701' and '20140701' THEN '3'
		   WHEN replace(date,'-','') between '20140701' and '20150701' THEN '4'
		   WHEN replace(date,'-','') between '20150701' and '20160701' THEN '5'
		   WHEN replace(date,'-','') between '20160701' and '20170701' THEN '6'
		   WHEN replace(date,'-','') between '20170701' and '20180701' THEN '7'
		   WHEN replace(date,'-','') between '20180701' and '20190701' THEN '8'
		   WHEN replace(date,'-','') between '20190701' and '20200701' THEN '9'
		   WHEN replace(date,'-','') between '20200701' and '20210701' THEN '10'
		   WHEN replace(date,'-','') between '20210701' and '20220701' THEN '11'
		   WHEN replace(date,'-','') between '20220701' and '20230701' THEN '12'
		   ELSE 'undefined'
		END as season_number
		,* from matches) m 
	on (t.id=m.away_team_id or t.id=m.home_team_id) 
group by league,name,season,season_number """

df=query_database(query_goals_scored_conceded)
print(df.head(5))

colormap=dict([(value,key) for key,value in enumerate(set(df["league"]))])
colors=[list(mcolors.CSS4_COLORS.values())[colormap[league]] for league in df["league"]]

fig, ax = plt.subplots()
ax.scatter(df["conceded"],df["scored"],
            c=colors)

#print(df.size)
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
plt.show()




#############################################################################


import pandas as pd
import bokeh.plotting as bpl
import bokeh.models as bmo
from bokeh.palettes import Turbo256 ,d3
#bpl.output_notebook()

source = bpl.ColumnDataSource(df)

# use whatever palette you want...
palette = Turbo256[len(df['league'].unique())]
color_map = bmo.CategoricalColorMapper(factors=df['league'].unique(),
                                   palette="Turbo256")

# create figure and plot
p = bpl.figure()
p.scatter(x='conceded', y='scored',
          color={'field': 'league', 'transform': color_map},
           source=source)
labels = bmo.LabelSet(
            x='conceded',
            y='scored',
            text='name',
            level='glyph',
            x_offset=5,
            y_offset=5,
            source=source,
            render_mode='canvas')

p.add_layout(labels)
bpl.output_file("/home/mstagl/vereinsdaten-analyzer/test.html", mode='inline')
bpl.save(p)
bpl.show(p)

#############################################################################

from bokeh.io import output_file, show, save
from bokeh.models import ColumnDataSource, HoverTool, LinearColorMapper
from bokeh.palettes import plasma
from bokeh.plotting import figure
from bokeh.transform import transform
from bokeh.models import ColorBar, LogColorMapper,Slider,CustomJS
from bokeh.layouts import column
from bokeh.models.widgets import Select
#source_ = bpl.ColumnDataSource(df)

hover = HoverTool(tooltips=[
    ("index", "$index"),
    ("Conceded","@conceded"),
    ("Scored", "@scored"),
    ('Team', '@name'),
    ('league','@league'),
    ('Season','@season')
])
#mapper = LinearColorMapper(palette=plasma(256), low=df['conceded'].min(), high=df['scored'].max())
colorpalettes=list(d3['Category20b'][20])
colorpalettes.extend([i for i in d3['Category20c'][20]])
palette = colorpalettes[:len(df['league'].unique())]
color_map = bmo.CategoricalColorMapper(factors=df['league'].unique(),
                                   palette=palette)

c = figure(plot_width=800, plot_height=1000, tools=[hover], title="BFV-TEAMS Season 2021/22")


for league in df["league"].unique().tolist():
    c.circle('conceded', 'scored', size=10, source=bpl.ColumnDataSource(df[(df["season_number"]=="11") & (df['league']==league)]),fill_color=transform('league', color_map), legend_label=league)
    pass


original_source = bpl.ColumnDataSource(df[df["season_number"]=="10"])

source_=bpl.ColumnDataSource(df)
#c.circle('conceded', 'scored', size=10, source=source_,fill_color=transform('league', color_map), legend_group='league')


print(df["season"].unique().tolist())
slides = Select(title="Option:", value = '1', options=df["season"].unique().tolist())
# Adding callback code
callback = CustomJS(args=dict(original_source=original_source,source_=source_),
                    code="""
    const data=original_source.data;
    const s_data = source_.data;
    const f = cb_obj.value;
    const x = data['conceded'];
    const y = data['scored'];
    const v = data['league'];
    const z = data['season'];
    console.log(z)
    console.log(f)
    for (let i = 0; i <= z.length; i += 1) {
        if (data['season'][i]==f){
            console.log(data['season'][i])
            x[i] = data['conceded'][i];
            y[i] = data['scored'][i];
            v[i] = data['league'][i];
            z[i] = data['season'][i];
        }
    }
    s_data['conceded'] = x;
    s_data['scored'] = y;
    s_data['league'] = v;
    s_data['season_number'] = z;
    source_.change.emit();
""")

callback2 = CustomJS(args=dict(original_source=original_source,source_=source_),
                    code="""
    var data = source_.data;                   
    var cat = cb_obj.value;
       
    if (cat == 'All'){                               
        data = source_.data;                                
    } else {                           
        var new_data = [];        
                          
        for (let i = 0; i <= source_.data['season'].length; i++){  
            console.log(source_.data['season'][i])   
            if (source_.data['season'][i] == cat) {    
                console.log(source_.data[][i])                                       
                new_data.push(source_.data[][i])  ;                                         
            }                                
                                            
        }                           
        data = new_data.data   ;                    
    }
    source_.data = data                     
    source_.change.emit();
""")
slides.js_on_change('value', callback2)



#color_bar = ColorBar(color_mapper=color_map, label_standoff=12)
#c.add_layout(color_bar, 'right')

c.legend.location = "top_right"
c.legend.click_policy="hide"

# Create Slider object
#slider = Slider(start=0, end=6, value=2,                step=0.2, title='Number of points')



#slider.js_on_change('value', callback)

# Arrange plots and widgets in layouts
from bokeh.embed import file_html
from bokeh.resources import CDN
#html = file_html(column(c), CDN, "my plot")

#with open("./plots/goals_scored_conced_2021-22.html","w") as f:
#    f.write(html)

bpl.output_file("./plots/goals_scored_conced_2021-22.html", mode='inline')
save(c)

#############################################################################



query_standings_per_league_season="""
-- select table for each round for each league for each season
SELECT rnk, points,league,name,*
FROM (
    SELECT
      ROW_NUMBER() OVER (
        PARTITION BY  league
        ORDER BY sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	)  DESC
      ) AS "rnk",sum(
	CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
	) As "Points",sum(
CASE WHEN homeresult==awayresult THEN 1 WHEN homeresult>awayresult and m.home_team_id==t.id THEN 3 WHEN homeresult<awayresult and m.away_team_id==t.id THEN 3 ELSE 0 END
) as points , count(*) as 'Number of Games', season,* 
	from  teams t join 
	(select substr(result,0,instr(result, ':')) as homeresult,
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
on (t.id=m.away_team_id or t.id=m.home_team_id) 
where season='2015/16'
group by m.league,t.name, season
order by league asc,points desc
) sub
ORDER BY
  season,league,rnk  ASC

"""









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