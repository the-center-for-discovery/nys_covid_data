import csv
import datetime 
import json
import pandas as pd
import pandas_bokeh as pb
import urllib.request as request
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import HoverTool
from math import pi

two_days = datetime.datetime.today() - datetime.timedelta(days=2)
one_day = datetime.datetime.today() - datetime.timedelta(days=1)

two_day_str = two_days.strftime("%Y-%m-%dT00:00:00.000")
one_day_str = one_day.strftime("%Y-%m-%dT00:00:00.000")

url_two = 'https://health.data.ny.gov/resource/xdss-u53e.json?test_date=' + two_day_str
url_one = 'https://health.data.ny.gov/resource/xdss-u53e.json?test_date=' + one_day_str

with request.urlopen(url_one) as response:
    source = response.read()
    data = json.loads(source)

if len(data) == 0:
    with request.urlopen(url_two) as response:
      source = response.read()
      data = json.loads(source)
else:
    data = json.loads(source)

with open ("covid.json", 'w') as outfile:
  json.dump(data, outfile)

with open('covid.json') as json_data:
    d = json.load(json_data)
    print(type(d))
    print(type(d[0]))
    print(json.dumps(d[0], indent=2, sort_keys = True))


filename = "County Stats.csv"
fw = open(filename, 'w')
cf = csv.writer(fw, lineterminator='\n')

cd = csv.writer(fw, lineterminator='\n')

# write the header
cf.writerow(["County", "New Positives", "All Positives", "New Tests", "All Tests"])

for counties in d:
  cnty = counties['county']
  date = counties['test_date']
  new_pos = counties['new_positives']
  cum_pos = counties['cumulative_number_of_positives']
  new_tests = counties['total_number_of_tests']
  cum_tests = counties['cumulative_number_of_tests']  
  if date == two_day_str:
    cf.writerow([cnty, new_pos, cum_pos, new_tests, cum_tests])
  elif date == one_day_str:
    cf.writerow([cnty, new_pos, cum_pos, new_tests, cum_tests])

fw.close()

df = pd.read_csv("County Stats.csv")

pct_pos = df["% Positive"]= (df["All Positives"] / df["All Tests"] * 100)

sur_cnt = df[df["County"].isin(["Delaware", "Sullivan", "Ulster", "Orange", "Greene", "Rockland"])]

p_test = sur_cnt.plot_bokeh.bar(x = 'County', y = ['New Tests', 'New Positives'], colormap = ['orange','red'],
                       title = 'New Tests - Sullivan County Area', xlabel = 'County', ylabel ='Tests/Cases',
                       figsize=(800, 600), zooming = False, panning = False, show_figure = False,
                        hovertool_string="""<h2> @{County} County</h2> 
                        <h3> New Tests: @{New Tests} </h3>
                        <h3> New Positives: @{New Positives} </h3>
                        <h3> Percentage Positives: @{% Positive} % </h3>""",)

p_case = sur_cnt.plot_bokeh.bar(x = 'County', y = ['New Positives'], colormap = ['red','orange'],
                       title = 'New Positive - Sullivan County Area', xlabel = 'County', ylabel ='New Positives',
                       figsize=(800, 600), zooming = False, panning = False,  show_figure = False,
                       hovertool_string="""<h2> @{County} County</h2> 
                        <h3> New Positives: @{New Positives} </h3>
                        <h3> Percentage Positives: @{% Positive} % </h3>""",)

plot = pb.plot_grid([[p_case, p_test]], plot_width=800, plot_height=600)

save(plot, filename='//discovery14/CovidHeatMap/status/Sullivan COVID Status.html')

p_all = df.plot_bokeh.bar(x = 'County', y = ['New Positives'], colormap = ['red','orange'],
                       title = 'New Positive - Sullivan County Area', xlabel = 'County', ylabel ='New Positives',
                       figsize=(1600, 800), zooming = False, panning = False, show_figure = False,
                       hovertool_string="""<h2> @{County} County</h2> 
                        <h3> New Positives: @{New Positives} </h3>
                        <h3> Percentage Positives: @{% Positive} % </h3>""",)

p_all.xaxis.major_label_orientation = pi/4

save(p_all, filename='//discovery14/CovidHeatMap/status/NYS COVID Status.html')
