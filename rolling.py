import csv
import datetime 
import json
import glob
import os
import numpy as np
import pandas as pd
import urllib.request as request
import pandas_bokeh
from bokeh.models import BoxAnnotation, Band
from bokeh.io import output_notebook
from bokeh.plotting import figure, output_file, show, save
from math import pi
from pandas import DataFrame

def urls():
    """
    Return list of urls [url_lst] to pull JSON data from https://health.data.ny.gov/
    """
    dat= []
    dat_str = []
    url_lst = []

    x = 0
    #set range for number of days to look at
    #create list of dates 
    for val in range(100):
        x += 1
        dat.append(datetime.datetime.today() - datetime.timedelta(days=x))
    #convert date varaibles to string 
    for d in dat:
        dat_str.append(d.strftime("%Y-%m-%dT00:00:00.000"))
    y = 0
    #create lists of url strings 
    for u in dat_str:
        url_lst.append('https://health.data.ny.gov/resource/xdss-u53e.json?test_date=' + dat_str[y])
        y += 1
    return(url_lst)

def make_csv():
    """
    Using urls() function querey https://health.data.ny.gov/ website for lay=test COVID data 

    Create list of JSON files conraining data

    Write JSON files to csv 
    """
    d = []
    index = 0
    #use request library to access NY state COVID API
    for url in urls():
        index +=1
        with request.urlopen(url) as response:
            source = response.read()
            data = json.loads(source)
    
            if len(data) == 0:
                continue

            with open ("covid.json", 'w') as outfile:
                json.dump(data, outfile)

            with open('covid.json') as json_data:
                j = json.load(json_data)
                d.append(j)
            
            fields = ["Date","County", "New_Positives", "All_Positives", "New_Tests", "All_Tests"]
            filename = f"County Stats {index}.csv"
            with open(filename, 'w') as fw:
                cf = csv.writer(fw, lineterminator='\n')
                # creatre header for csv files 
                cf.writerow(fields)
                for counties in data:   
                    date = counties['test_date']
                    cnty = counties['county']
                    new_pos = counties['new_positives']
                    cum_pos = counties['cumulative_number_of_positives']

                    new_tests = counties['total_number_of_tests']
                    cum_tests = counties['cumulative_number_of_tests']
                    cf.writerow([date,cnty, new_pos, cum_pos, new_tests, cum_tests])

make_csv()

def df30():
    """
    Concatanate the multiple csv files and create Dataframe for visualizations 
    """

    fout=open("30day.csv","a")
    # now the rest:    
    i = 0
    for num in range(i,30):
        i += 1
        f = open("County Stats "+str(i)+".csv")
        f.__next__()  # skip the header
        for line in f:
            fout.write(line)

    df  = pd.read_csv("30day.csv", names=["Date", "County", "New_Positives", "All_Positives", "New_Tests", "All_Tests"])

    df.sort_values(by='Date', inplace=True, ascending=True)

    for col in df.select_dtypes(include=[object]):
        df[col] = df[col].str.slice(0, 10)
    
    pct_pos = df["Positive"]= (df["New_Positives"] / df["New_Tests"] * 100)
    sul30 = df[df['County'].isin(["Sullivan", "Ulster", "Orange", "Rockland"])]

    sul30 = sul30.pivot_table(index='Date',columns='County',values='Positive',)

    sul30 = DataFrame(sul30)

    return sul30

def df100():
    """
    Concatanate the multiple csv files and create Dataframe for visualizations 
    """

    fout=open("100day.csv","a")
    # now the rest:    
    i = 0
    for num in range(1,100):
        i += 1
        f = open("County Stats "+str(i)+".csv")
        f.__next__()  # skip the header
        for line in f:
            fout.write(line)

    df  = pd.read_csv("100day.csv", names=["Date", "County", "New_Positives", "All_Positives", "New_Tests", "All_Tests"])

    df.sort_values(by='Date', inplace=True, ascending=True)

    for col in df.select_dtypes(include=[object]):
        df[col] = df[col].str.slice(0, 10)
    
    pct_pos = df["Positive"]= (df["New_Positives"] / df["New_Tests"] * 100)
    sul100 = df[df['County'].isin(["Sullivan", "Ulster", "Orange", "Rockland"])]

    sul100 = sul100.pivot_table(index='Date',columns='County',values='Positive',)

    sul100 = DataFrame(sul100)

    return sul100

def plot_lines():
    """
    Create line graph for rolling dataset
    
    Return html file 
    """
    tooltips = [("County","@County"),("% Positive","@Positive")]

    #make 30 day plot
    p30 = df30().plot_bokeh(kind="line", figsize = (1600,800), alpha = 1, panning = False, zooming = False, ylim = (0,15), show_average = False, rangetool = False,
                        xlabel = "Date", ylabel = 'Positive', title = "Percentage Positve - Rolling 30 Days", hovertool = True, colormap = ('orange', 'green', 'red', 'purple'))

    p30.xaxis.major_label_orientation = pi/4

    grn_box = BoxAnnotation(top=3.5, fill_alpha=0.1, fill_color='green')
    yel_box = BoxAnnotation(bottom = 3.5, top=4.5, fill_alpha=0.1, fill_color='yellow')
    ong_box = BoxAnnotation(bottom = 4.5, top=5.5, fill_alpha=0.1, fill_color='orange')
    red_box = BoxAnnotation(bottom=5.5, fill_alpha=0.1, fill_color='red')
    p30.add_layout(grn_box)
    p30.add_layout(yel_box)
    p30.add_layout(ong_box)
    p30.add_layout(red_box)

    save(p30, filename='status/30days.html')

    #make 100 day plot 
    p100 = df100().plot_bokeh(kind="line", figsize = (1600,800), alpha = 1, panning = False, zooming = False, ylim = (0,15), show_average = False, rangetool = True,
                        xlabel = "Date", ylabel = 'Positive', title = "Percentage Positve - Rolling 100 Days", hovertool = True, colormap = ('orange', 'green', 'red', 'purple'))

    save(p100, filename='status/100days.html')

if __name__ == "__main__":
    plots()