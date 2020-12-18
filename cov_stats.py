import csv
import datetime 
import json
import pandas as pd
import pandas_bokeh as pb
import urllib.request as request
from bokeh.plotting import figure, output_file, show, save
from bokeh.models import HoverTool
from math import pi

class EST5EDT(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5) + self.dst(dt)

    def dst(self, dt):
        d = datetime.datetime(dt.year, 3, 8)  # 2nd Sunday in March
        self.dston = d + datetime.timedelta(days=6-d.weekday())
        d = datetime.datetime(dt.year, 11, 1)  # 1st Sunday in Nov
        self.dstoff = d + datetime.timedelta(days=6-d.weekday())
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(0)

    def tzname(self, dt):
        return 'EST5EDT'

t_est = datetime.datetime.now(tz=EST5EDT())
t_str = t_est.strftime("%Y-%m-%d, %H:%M:%S")

one_day = datetime.datetime.today() - datetime.timedelta(days=1)
two_days = datetime.datetime.today() - datetime.timedelta(days=2)
thr_days = datetime.datetime.today() - datetime.timedelta(days=3)

one_day_str = one_day.strftime("%Y-%m-%dT00:00:00.000")
two_day_str = two_days.strftime("%Y-%m-%dT00:00:00.000")
thr_day_str = thr_days.strftime("%Y-%m-%dT00:00:00.000")

url_one = 'https://health.data.ny.gov/resource/xdss-u53e.json?test_date=' + one_day_str
url_two = 'https://health.data.ny.gov/resource/xdss-u53e.json?test_date=' + two_day_str
url_thr = 'https://health.data.ny.gov/resource/xdss-u53e.json?test_date=' + thr_day_str

url_lst = [url_one,url_two,url_thr]

def get_json():
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
  return d

def make_csv():

    filename = "base_files/County Stats.csv"
    with open(filename, 'w') as fw:
        cf = csv.writer(fw, lineterminator='\n')
        # write the header
        cf.writerow(["County", "New_Positives", "All_Positives", "New_Tests", "All_Tests"])

        for counties in get_json():
            date = counties['test_date']
            if date in [two_day_str, one_day_str]:
                cnty = counties['county']
                new_pos = counties['new_positives']
                cum_pos = counties['cumulative_number_of_positives']
                new_tests = counties['total_number_of_tests']
                cum_tests = counties['cumulative_number_of_tests']
                cf.writerow([cnty, new_pos, cum_pos, new_tests, cum_tests])

make_csv()

def plots():
  df = pd.read_csv("County Stats.csv")

  pct_pos = df["Positive"]= (df["New_Positives"] / df["New_Tests"] * 100)
  sur_cnt = df[df["County"].isin(["Delaware", "Sullivan", "Ulster", "Orange", "Greene", "Rockland"])]

  p_test = sur_cnt.plot_bokeh.bar(x='County', y=['New_Positives', 'New_Tests'], colormap=['red', 'orange'],
                                  title='New_Tests - Sullivan County Area, Data as of: ' + t_str, xlabel='County', ylabel='Tests/Cases',
                                  figsize=(800, 600), zooming=False, panning=False, show_figure=False, stacked=True,
                                  hovertool_string="""<h2> @{County} County</h2> 
                          <h3> New_Tests: @{New_Tests} </h3>
                          <h3> New_Positives: @{New_Positives} </h3>
                          <h3> Percentage Positives: @{Positive} % </h3>""", alpha=0.6,)

  p_pct = sur_cnt.plot_bokeh.bar(x='County',  y=['Positive'], stacked=False, normed=100, colormap=['red', 'orange'],
                                 title='Percentage Positive Sullivan County Area, Data as of: ' + t_str, xlabel='County', ylabel='Tests/Cases',
                                 figsize=(800, 600), zooming=False, panning=False, show_figure=False,
                                 hovertool_string="""<h2> @{County} County</h2> 
                          <h3> All_Positives: @{All_Positives} </h3>
                          <h3> Percentage Positives: @{Positive} % </h3>""", alpha=0.6)

  plot = pb.plot_grid([[p_test, p_pct]], plot_width=800, plot_height=600)

  output_file('Sullivan COVID Status.html')
  save(plot, filename='status/Sullivan COVID Status.html')

  p_all = df.plot_bokeh.bar(x='County', y=['New_Positives'], colormap=['red', 'orange'],
                            title='Testing Status - NY State, Data as of: ' + t_str, xlabel='County', ylabel='New_Positives',
                            figsize=(1600, 800), zooming=False, panning=False, show_figure=True,
                            hovertool_string="""<h2> @{County} County</h2>
                          <h3> New_Positives: @{New_Positives} </h3>
                          <h3> Percentage Positives: @{Positive} % </h3>""", stacked=True, alpha=0.6)

  p_all.xaxis.major_label_orientation = pi/4

  output_file('NYS COVID Status.html')
  save(p_all, filename='status/NYS COVID Status.html')


if __name__ == "__main__":
  plots()
