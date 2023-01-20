import altair as alt
import pandas as pd
import sys
import os
import tempfile
import io
import pydoc 
import shutil
from flask import Flask
from flask import render_template
from flask import request


app = Flask(__name__)


def plot_reported_cases(county, start=None, end=None):
    """ Method to plot a bar plot for reported Covid-19 cases in a county

    Args:
        county (str): Link for the county to plot cases for
        start (str): Optional start-time to plot cases from  
        end (str): Optional end-time to plot cases from

    Returns:
        chart (plot): The plot over reported cases
    """        
    
    county_dataframe = pd.read_csv(county, sep=";")
    """ Dato is read as an object instead of datetime, changing this with to_datetime """
    county_dataframe["Dato"] = pd.to_datetime(county_dataframe["Dato"], format="%d.%m.%Y")

    """ specifying the dates plotted """
    if start is not None and end is not None:
        try:
            mask = (county_dataframe["Dato"] >= start) & (county_dataframe["Dato"] <= end)
            county_dataframe = county_dataframe.loc[mask]
        
        except (TypeError):
            print("Invalid datetime. Full length chosen")
            

    """ plot the chart """
    chart = alt.Chart(county_dataframe).mark_bar(size=10, opacity=0.5).encode(
        x="Dato:T",
        y="Nye tilfeller",
        tooltip=["Dato", "Nye tilfeller"]
        ).properties(
            title="Antall meldte covid-19 tilfeller",
            height=360,
            width=800,
        ).interactive()

    #chart.show()
    return chart

    #dayfirst=True under parsing av data ved mangel på data


def plot_cumulative_cases(county, start=None, end=None):
    """ Method to plot a line plot for cumulative cases of Covid-19 in a county

    Args:
        county (str): Link for the county to plot cases for
        start (str): Optional start-time to plot cases from  
        end (str): Optional end-time to plot cases from

    Returns:
        chart (plot): The plot over cumulative cases
    """

    county_dataframe = pd.read_csv(county, sep=";")
    """ Dato is read as an object instead of datetime, changing this with to_datetime """
    county_dataframe["Dato"] = pd.to_datetime(county_dataframe["Dato"], format="%d.%m.%Y")

    """ specifying the dates plotted """
    if start is not None and end is not None:
        try:
            mask = (county_dataframe["Dato"] >= start) & (county_dataframe["Dato"] <= end)
            county_dataframe = county_dataframe.loc[mask]
        
        except (TypeError):
            print("Invalid datetime. Full length chosen")


    chart = alt.Chart(county_dataframe).mark_line(color="#fc2008").encode(
        x="Dato:T", 
        y="Kumulativt antall",
        tooltip=["Dato", "Kumulativt antall"]
        ).properties(
            title="Antall meldte covid-19 tilfeller",
            height=360,
            width=800,
        ).interactive()

    #chart.show()
    return chart


def plot_both(county, start=None, end=None):
    """ Plot both the line and bar graphs into one graph

    Args:
        county (str): Link for the county to plot cases for
        start (str): Optional start-time to plot cases from  
        end (str): Optional end-time to plot cases from
    
    Returns:
        chart (plot): The combined plot over reported and cumulative cases
    """

    """ get the reported and cumulative plots """
    reported_chart = plot_reported_cases(county, start, end)
    cumulative_chart = plot_cumulative_cases(county, start, end)

    """ Layer the graphs together in one plot, with indepentent y-axis """
    #chart = alt.layer(reported_chart, cumulative_chart).resolve_scale(y="independent")
    chart = alt.layer(cumulative_chart, reported_chart).resolve_scale(y="independent")

    return chart


def plot_norway(link):
    """ Plot a map over the norwegian counties and their amount of covid-19 cases

    Args:
        link (str): Link for the amount of cases per county

    Returns:
        chart (plot): The interactive map over norwegian counties
    """

    data = {"Category": [],
            "Insidens": []}

    """ retrieve the data from the csv file and add it to a dict """
    file = io.open(link, mode="r", encoding="utf-8")
    next(file) #skip first line
    for line in file:
        split = line.split(";")
        county = split[0].strip().replace("\"", "")
        insidens = split[1].strip().replace(",", ".")
        data["Category"].append(county)
        data["Insidens"].append(float(insidens))

    norway_dataframe = pd.DataFrame.from_dict(data)

    """ get the topology of norwegian counties """
    counties = alt.topo_feature("https://raw.githubusercontent.com/deldersveld/topojson/master/countries/norway/norway-new-counties.json", "Fylker")

    """ defining the selection for highlighting a county """
    selection = alt.selection(type="single", on="mouseover", fields=["properties.navn"], empty="none")

    """ plotting the map """
    chart = alt.Chart(counties).mark_geoshape().encode(
        tooltip=[
            alt.Tooltip("properties.navn:N", title="County"),
            alt.Tooltip("Insidens:Q", title="Cases per 100k"),
        ],
        color=alt.Color("Insidens:Q", scale=alt.Scale(scheme="reds"),
                        legend=alt.Legend(title="Cases per 100k capita")),
        stroke=alt.condition(selection, alt.value("gray"), alt.value(None)),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.8)),
    ).transform_lookup(
        lookup="properties.navn",
        from_=alt.LookupData(norway_dataframe, "Category", ["Insidens"]),
    ).properties(
        width=600,
        height=800,
        title="Number of covid-19 cases per 100k in every county",
    ).add_selection(
        selection
    )

    return chart 


@app.route("/graph.json")
def flask_plot_graph_json():    
    """ The graphs for all counties. This is shown when the website is opened.
    Combines the three different types of graphs and convert the plot to json 
    
    Returns:
        (str): string-representation of the graphs combined into one .json file
    """
    
    """ path to directory with csv-files """
    dir_path = "./reported_cases/"

    for file in os.listdir(dir_path):
        filename = os.fsdecode(file)

        """ all counties """
        if "(" not in filename:
            complete_path = os.path.join(dir_path, filename)
            
            fig_both = plot_both(complete_path)
            fig_cum = plot_cumulative_cases(complete_path)
            fig_rep = plot_reported_cases(complete_path)
            
    combined = alt.vconcat(fig_both, fig_cum, fig_rep)

    """ flask representation requires html or json """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    combined.save(tmp.name)

    with open(tmp.name) as file:
        return file.read()

    """ closing and deleting the tempfile """
    tmp.close()
    os.unlink(tmp.name)


@app.route("/county", methods=["POST"])
def flask_plot_graph_reselect():    
    """ The graphs for a selected county.
    Combines the three different types of graphs and convert the plot to json 
    
    Returns:
        (str): string-representation of the graphs combined into one .json file
    """
    
    """ path to directory with csv-files """
    dir_path = "./reported_cases/"

    """ choice of county from the dropdown menu in the graph.html file """
    county_choice = request.form.get("county")
    print(county_choice)

    #if county choice == NULL, all counties

    for file in os.listdir(dir_path):
        filename = os.fsdecode(file)

        if county_choice in filename:
            """ found the county """
            complete_path = os.path.join(dir_path, filename)
            
            fig_both = plot_both(complete_path)
            fig_cum = plot_cumulative_cases(complete_path)
            fig_rep = plot_reported_cases(complete_path)

        elif "(" not in county_choice:
            """ all counties """
            complete_path = os.path.join(dir_path, filename)
            
            fig_both = plot_both(complete_path)
            fig_cum = plot_cumulative_cases(complete_path)
            fig_rep = plot_reported_cases(complete_path)

    combined = alt.vconcat(fig_both, fig_cum, fig_rep)

    """ flask representation requires html or json """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    combined.save(tmp.name)

    with open(tmp.name) as file:
        return file.read()

    """ closing and deleting the tempfile """
    tmp.close()
    os.unlink(tmp.name)


@app.route("/map.json")
def flask_plot_map_json():
    """ Turns the map into a .json file 
    
    Returns:
        (str): string-representation of the map-plot as a .json file
    """

    chart = plot_norway("antall-meldte-tilfeller.csv")

    """ flask representation requires html or json """
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    chart.save(tmp.name)

    with open(tmp.name) as file:
        return file.read()

    """ closing and deleting the tempfile """
    tmp.close()
    os.unlink(tmp.name)


@app.route("/")
def flask_plot_graph():   
    """ The webpage for the graphs 
    
    Returns:
        the render of the graph-plots
    """

    return render_template("graph.html")


@app.route("/map")
def flask_plot_map():
    """ The webpage for the map over Norway 
    
    Returns:
        the render of the map-plot
    """
    
    return render_template("map.html")


@app.route("/help")
def flask_plot_help():
    """ Generates a documentation page for the whole Python file with pydoc
    
    Returns:
        the render of the pydoc help-page
    """
    
    pydoc.writedoc("web_visualization")
    shutil.move("web_visualization.html", "templates/web_visualization.html") #move to another directory

    return render_template("web_visualization.html")


def main(param):
    """ Main program where you either run a terminal-program (6.1), 
        or a interactive virtualization on a website is created 

    Args:
        param (list): list of the terminal arguments. If an argument is given, 
                      the terminal program for 6.1 will be run
    
    Returns:
        chart (plot): The plot for either reported, cumulative or both combined.
                      The plot can both be county and time-restricted
    """

    if len(param) != 2:
        """ Interactive visualization """ 
        app.run(debug=True)

    else:
        """ Terminal program """
        graph = input("Choose your implementation: \n" \
                        "Type 1 for reported cases by day\n" \
                        "Type 2 for cumulative cases\n" \
                        "Type 3 for both\n")

        county = input("Choose a county (optional): \n" \
                        "1 - Agder\n" \
                        "2 - Innlandet\n" \
                        "3 - Møre og Romsdal\n" \
                        "4 - Nordland\n" \
                        "5 - Oslo\n" \
                        "6 - Rogaland\n" \
                        "7 - Troms og Finnmark\n" \
                        "8 - Trøndelag\n" \
                        "9 - Vestfold og Telemark\n" \
                        "10 - Vestland\n" \
                        "11 - Viken\n")
        
        start = input("Choose start-time in ymd-format (optional):")
        if start == "":
            start = None
            end = None 

        else:
            end = input("Choose end-time in ymd-format:\n")
            while end == "":
                print("You are required to choose an end-time")
                end = input("Choose end-time in ymd-format:\n")

        """ path to directory with csv-files """
        dir_path = "./reported_cases/"

        for file in os.listdir(dir_path):
            filename = os.fsdecode(file)

            """ if the number given by the user matches any of the counties """
            if ("(" + county + ")") in filename:
                complete_path = os.path.join(dir_path, filename)
                if graph == "3":
                    fig = plot_both(complete_path, start, end)
                elif graph == "2":
                    fig = plot_cumulative_cases(complete_path, start, end)
                else:
                    fig = plot_reported_cases(complete_path, start, end)
                
            elif "(" not in filename:
                """ all counties """
                complete_path = os.path.join(dir_path, filename)
                if graph == "3":
                    fig = plot_both(complete_path, start, end)
                elif graph == "2":
                    fig = plot_cumulative_cases(complete_path, start, end)
                else:
                    fig = plot_reported_cases(complete_path, start, end)
        

        fig.show()


if __name__ == "__main__":
    param = sys.argv
    main(param)