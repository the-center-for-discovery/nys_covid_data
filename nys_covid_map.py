import numpy as np
import pandas as pd
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure, ColumnDataSource, save
from bokeh.tile_providers import get_provider, Vendors
from bokeh.palettes import Reds
from bokeh.transform import linear_cmap,factor_cmap
from bokeh.layouts import row, column
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar, NumeralTickFormatter

df_stats = pd.read_csv('base_files/County Stats.csv')
df_coords = pd.read_csv('base_files/coords.csv')

df_stats['County'] = df_stats['County'].astype(str) + ", NY"
pct_pos = df_stats["Positive"]= (df_stats["New_Positives"] / df_stats["New_Tests"] * 100)

df = pd.merge(df_stats, df_coords, left_on='County', right_on='County')

df.head()
df = df[df['County'].isin(["Delaware, NY","Sullivan, NY", "Ulster, NY", "Orange, NY", "Rockland, NY", "Broome, NY", "Chenango, NY", "Otsego, NY", ])]

# Define function to switch from lat/long to mercator coordinates
def x_coord(x, y):
    
    lat = x
    lon = y
    
    r_major = 6378137.000
    x = r_major * np.radians(lon)
    scale = x/lon
    y = 180.0/np.pi * np.log(np.tan(np.pi/4.0 + 
        lat * (np.pi/180.0)/2.0)) * scale

    print(x,y)
    return (x, y)

# Define coord as tuple (lat,long)
df['coordinates'] = list(zip(df['latitude'], df['longitude']))

# Obtain list of mercator coordinates
mercators = [x_coord(x, y) for x, y in df['coordinates']]

# Create mercator column in our df
df['mercator'] = mercators

# Split that column out into two separate cols - mercator_x and mercator_y
df[['mercator_x', 'mercator_y']] = df['mercator'].apply(pd.Series)

# Drop 'geometry' column 
df = df.drop(columns=['geometry'])

# Select tile set to use
chosentile = get_provider(Vendors.CARTODBPOSITRON_RETINA)

myReds = ['#FFCCBB', '#FF6C5C', '#F85C4D', '#E84C3D', '#D83C2D', '#BF0000']


# Choose palette
palette = myReds

# Reds[3].reverse()

# Tell Bokeh to use df as the source of the data
def plot_map():
# Tell Bokeh to use df as the source of the data
    source = ColumnDataSource(data=df)

    # Define color mapper - which column will define the colour of the data points
    color_mapper = linear_cmap(field_name = 'Positive', palette = palette, low = df['Positive'].min(), high = df['Positive'].max())

    # Set tooltips - these appear when we hover over a data point in our map, very nifty and very useful
    nan_color = '#d9d9d9'
    tooltips = [("County","@County"),("Positive (%)","@Positive"),("New_Positives", "@New_Positives"), ("New_Tests", "@New_Tests")]

    # Create figure
    p = figure(title = 'COVID % Posivity Rates - Sullivan County Area', x_axis_type="mercator", y_axis_type="mercator", 
            x_axis_label = 'Longitude', y_axis_label = 'Latitude', tooltips = tooltips, plot_width=1600, plot_height=900,
            x_range=(-9138712.3831, -7948900.2442), y_range=(4926497.0280, 5538604.7505), )
            
    # Add map tile
    p.add_tile(chosentile)

    # Add points using mercator coordinates
    p.circle(x = 'mercator_x', y = 'mercator_y', color = color_mapper, source=source, size=50, fill_alpha = 0.8)

    #Defines color bar
    color_bar = ColorBar(color_mapper=color_mapper['transform'], 
                        formatter = NumeralTickFormatter(format='0.0[0000]'), 
                        label_standoff = 13, width=8, location=(0,0))

    # Set color_bar location
    p.add_layout(color_bar, 'right')

    # Display in notebook
    output_notebook()

    # Save as HTML
    output_file('status/COVID_map.html', title='COVID % Posivity Rates - Sullivan County Area')
    save(p, filename='status/COVID_map.html')

if __name__ == "__main__":
    plot_map()