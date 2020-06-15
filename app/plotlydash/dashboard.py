"""Create a Dash app within a Flask app."""
import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from .layout import html_layout
import plotly.graph_objects as go
from app.functions import reset_sets_list, get_data
from dash.dependencies import Input, Output, State
import datetime

def create_dashboard(server):
    #Need a background version of dataframe to set options for the date dropdown
    tracks_bg = pd.read_csv('https://jroefive.github.io/track_length_combined')

    #Sets hard assigned for the default show (Big Cypress)
    sets = ['Set 1', 'Set 2']

    #Add Year, Month, and Day columns to the dataframe to make the dropdowns dynamic (You only get options for the months played in the chosen year)
    tracks_bg['year'] = pd.DatetimeIndex(tracks_bg['date']).year
    tracks_bg['month'] = pd.DatetimeIndex(tracks_bg['date']).month
    tracks_bg['day'] = pd.DatetimeIndex(tracks_bg['date']).day

    #Create lists for dropdowns for all shows and all years.
    all_dates = tracks_bg['date'].unique()
    all_years = tracks_bg['year'].unique()

    #Initiate the dashboard
    dash_app = dash.Dash(server=server,
                         routes_pathname_prefix='/dashapp/',
                         external_stylesheets=['/app/static/dist/css/styles.css']
                         )

    #Pull in defaul html saved in layout.py
    dash_app.index_string = html_layout
    #Create overall layout
    dash_app.layout = html.Div([
            # Input window for dates and graph options.
            html.Div([
                #Date inputs
                html.Div([
                    html.Div([
                        html.P('Option 1: Choose show from top list of all possible shows.', style={'color': '#F15A50', 'font-family': 'Arial'}),
                        html.P('Option 2: Choose show by choosing year, month, day separately.', style={'color': '#F15A50', 'font-family': 'Arial'})],
                    style={'text-align': 'center'}),
                    dcc.Dropdown(id='Show_Date',
                        options=[{'label': i, 'value': i} for i in all_dates],
                        value='1999-12-31'),
                    html.Div([
                    dcc.Dropdown(id='Show_Year',
                        options=[{'label': i, 'value': i} for i in all_years],
                        placeholder="Select Year")],
                    style={'width': '33.33%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(id='Show_Month',placeholder="Select Month (after year)")],
                        style={'width': '33.33%', 'display': 'inline-block'}),
                    html.Div([
                        dcc.Dropdown(id='Show_Day',placeholder="Select Day (after month)")],
                        style={'width': '33.33%', 'display': 'inline-block'})],
                style={'width': '50%', 'display': 'inline-block', 'font-family': 'Arial'}),
                #Graph options inputs
                html.Div([
                    dcc.Dropdown(
                        id='Set',
                        options=[{'label': i, 'value': i} for i in sets],
                        value='Set 1'),
                    dcc.Dropdown(id='Graph_Type',
                        options=[{'label': 'Graph Type - Song Duration', 'value': 'Song Duration'},
                                 {'label': 'Graph Type - Set Placement', 'value': 'Set Placement'}],
                        value='Song Duration')],
                style = {'width': '25%', 'display': 'inline-block', 'font-family': 'Arial'}),
                html.Div([
                    dcc.Dropdown(
                        id='points_to_show',
                        options=[{'label': 'Show Points for All Times Played', 'value': 'all'},
                                 {'label': 'Show Points only for Outliers', 'value': 'outliers'},
                                 {'label': 'Show only Box Plot', 'value': False}],
                        value='all'),
                    dcc.Dropdown(id='shows_to_highlight',
                        options=[{'label': 'None', 'value': 'None'},
                            {'label': 'Highlight Previous 50 Shows', 'value': 'Previous 50 Shows'},
                            {'label': 'Highlight Selected Show', 'value': 'Selected Show'},
                            {'label': 'Highlight Next 50 Shows', 'value': 'Next 50 Shows'}],
                        value='Selected Show')],
                    style = {'width': '25%', 'display': 'inline-block', 'font-family': 'Arial'})],
                style={'width': '90%', 'margin-left':'75px', 'backgroundColor':'#2C6E91'}),
                #Graph placement
                dcc.Graph(id='graph_with_input')],
        style={'text-align': 'center','backgroundColor':'#2C6E91'})

    #Update the month options after a year is chosen
    @dash_app.callback(
        Output('Show_Month', 'options'),
        [Input('Show_Year', 'value')])
    def set_month_options(show_year):
        month_options_pd = tracks_bg[tracks_bg['year']==show_year].copy()
        month_options = month_options_pd['month'].unique()
        return [{'label': i, 'value': i} for i in month_options]

    #Update the day options once a month is chosen.
    @dash_app.callback(
        Output('Show_Day', 'options'),
        [Input('Show_Year', 'value'),
         Input('Show_Month', 'value'),])
    def set_day_options(show_year, show_month):
        day_options_pd = tracks_bg[(tracks_bg['year']==show_year) & (tracks_bg['month']==show_month)].copy()
        day_options = day_options_pd['day'].unique()
        return [{'label': i, 'value': i} for i in day_options]

    #Reset show_date once a day is chosen
    @dash_app.callback(
        Output('Show_Date', 'value'),
        [Input('Show_Day', 'value'),
        Input('Show_Year', 'value'),
        Input('Show_Month', 'value')])
    def set_date(day, year, month):
        show_date = datetime.date(year, month, day)
        return show_date

    #Reset list of sets every time a show_date is changed
    @dash_app.callback(
        Output('Set', 'options'),
        [Input('Show_Date', 'value')])
    def set_month_options(show_date):
        sets = reset_sets_list(show_date)
        return [{'label': i, 'value': i} for i in sets]

    #Redraw figure every time any of the inputs change
    @dash_app.callback(
        Output('graph_with_input', 'figure'),
        [Input('Set', 'value'),
         Input('Graph_Type', 'value'),
         Input('Show_Date', 'value'),
         Input('points_to_show', 'value'),
         Input('shows_to_highlight', 'value')])
    def draw_fig(set, graph_type, show_date, points_to_show, shows_to_highlight):
        #Call the get_date function to get the setlist and two graph input dictionaries
        graph_data_dict, set_songs, graph_highlight_dict = get_data(set, graph_type, show_date, shows_to_highlight)

        #Initiate the figrue
        figure = go.Figure()

        #Iterate through all songs in the set and create a boxplot trace for that song
        for song in set_songs:
            figure.add_trace(go.Box(
                y=graph_data_dict[song],
                name=song,
                #Inclue all points, or outliers, or just the box plot based on dropdown input
                boxpoints=points_to_show,
                #Overlay points and box to keep graph compact
                pointpos=0,
                #Include the mean and standard deviation in box plot
                boxmean='sd',
                #Set points to spread out a bit
                jitter=.8,
                #Set markers to be donuts and have the same blue color as the official Phish donut logo
                marker=dict(color="#2C6E91", symbol='circle-open', opacity=0.5, line_width=2),
                marker_size=4))

            #As long as the highlighted shows isn't None, draw a second trace that only includes the chosen shows
            if shows_to_highlight != 'None':
                figure.add_trace(go.Box(
                    y=graph_highlight_dict[song],
                    name=song,
                    boxpoints=points_to_show,
                    pointpos=0,
                    jitter=.6,
                    #Set markers to be a bit bigger and the red donut color
                    marker=dict(color='#F15A50', symbol='circle-open', opacity=0.5, line_width=2),
                    line_width = 0.5,
                    marker_size=7.5))

        #Basic layout for graph
        figure.update_layout(
            yaxis=dict(
                autorange=True,
                automargin=True,
                showgrid=True,
                zeroline=True,
                dtick=5,
                gridcolor='rgb(255, 255, 255)',
                gridwidth=1,
                zerolinecolor="#2C6E91",
                zerolinewidth=2,),
            margin=dict(l=100, r=40, t=40, b=40),
            paper_bgcolor="#2C6E91",
            font=dict(
                family="Arial, monospace",
                size=18,
                color='#F15A50'),
            showlegend=False)

        #For the set placement graphs, eset the numerical values of the y tick labels to match what they mean in context
        if graph_type == 'Set Placement':
            figure.update_layout(
                yaxis=dict(
                    tickmode='array',
                    tickvals=[1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5],
                    ticktext=['Start Set 1', 'Mid Set 1', 'Start Set 2', 'Mid Set 2', 'Start Set 3', 'Mid Set 3', 'Start Encore', 'Mid Encore', 'End of Show']))

        #If it is the song duration graph, set the y axis label correctly
        else:
            figure.update_layout(yaxis_title="Song Duration in Minutes",)
        return figure

    return dash_app.server
