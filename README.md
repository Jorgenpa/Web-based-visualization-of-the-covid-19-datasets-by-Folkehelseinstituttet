## Web-based Visualizations of the Covid-19 Datasets by Folkehelseinstituttet
The assignment is based around building a web-based visualization of the covid-19 datasets by Folkehelseinstituttet (FHI). The user has a choice between interacting with a web-based service or a terminal program. The data can be limited to counties and time-range. 

The names of the data-files (.csv) are not modified for the assignment, so if more recent datasets are wanted, download them and replace the files in the reported_cases folder.
All the tasks will still work with newer datasets. 
Last retrieved datasets: 2020.11.09

## Requirements
The assignment was made with Python 3.8, and on a Windows OS. 
It has been tested to run on Linux based OS. 

- Altair vega_datasets. A visualization libary for Python. Includes Pandas and more. Version 4.1.0
- Altair_viewer. Viewer for Altair (required for visualizing the graph in 6.1). Version 0.3.0
- Pandas. Tool for data analysis, time series and statistics. Version 1.0.5
- Flask. A framework for building complex web applications. Version 1.1.2

The package manager pip can be used to install the packages:
```bash
pip install <package>
```

Packages: Altair vega_datasets, Altair_viewer, Pandas, Flask

## Usage
# 6.1 Cases Over Time Plotter
The script is run with the terminal-command:
```bash
py web_visualization.py <argument>
```

Where <argument> can be whatever as long as you write something (or else the interactive visualization will run instead)

"Graphtype" is either "reported" or "cumulative".
It is optional to select county and time-range.
Default county is all counties, and default time-range is the whole lifespan.
Time-range must be written in ymd.

# 6.2-6.5 Interactive Visualization and Documentation
The script first needs to be run with the terminal command:
```bash
py web_visualization.py 
```

You will then be presented with a link:
```bash
https://127.0.0.1:5000/
``` 

That link brings you to the webpage, where you can see the different covid-19 graphs for the whole country, choose a county, or show cases on a map. There is also a documentation page, press the "Hjelp" button in the header to get there.

# 6.6 Challenge - Creating an Interactive Map
The bonus task is implemented into the webpage. It can be reached by pressing the "Kart" button in the header.
Last retrieved dataset: 2020.11.11

