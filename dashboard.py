import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd  
import plotly.express as px  
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
import os
import tkinter as tk 
from tkinter import Label
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




# Loading the dataset 
data_path = 'C:\\Users\\Owner\\Cos7008\\Merge_DataSet.csv'

if not os.path.exists(data_path):
    raise FileNotFoundError(f"The file {data_path} does not exist.")
merged_df1 = pd.read_csv(data_path)

# Print  DataFrame for d bug
print(merged_df1.head())  
print(merged_df1.info())  

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
# App layout
app.layout = html.Div(children=[
    html.H1(children='TechSafe: Threat Actor Scoring Dashboard'),
    dcc.Dropdown(
        id='threat-dropdown-menu',
        options=[{'label': threat, 'value': threat} for threat in merged_df1['name'].unique()],
        placeholder='Select a threat actor'
    ),
    html.Div(id='threat-details'),
    # tab
    dcc.Tabs(id='graph-tabs', value='bar', children=[
        dcc.Tab(label='Line Chart', value='bar'),
        dcc.Tab(label='Heat Map', value='heatmap'),
        dcc.Tab(label='Pie chart', value='pie'),
    ]),
    html.Div(id='graph-content'),
])


@app.callback(
    Output('graph-content', 'children'),
    Input('graph-tabs', 'value')
)
def tab_content(pick_tab):
    if pick_tab == 'bar':
        # Placeholder bar graph (you can customize it with appropriate x, y values)
        bar_fig = px.bar(merged_df1, x='name', y='complexity_score',
                         title="Complexity Score by Threat Actor",
                         labels={'complexity_score': 'Complexity Score', 'name': 'Threat Actor'})
        return dcc.Graph(id='bar-graph', figure=bar_fig)

    elif pick_tab == 'heatmap':
        # Create heatmap using seaborn
        plt.figure(figsize=(10, 8))
        techniques_one_hot = pd.get_dummies(merged_df1['technique'])
        corr_matrix = techniques_one_hot.corr()
        sns.heatmap(corr_matrix, annot=False, cmap='coolwarm')
        plt.title('Heatmap of Technique Correlations')

        # Save the plot to a PNG image
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        encoded_image = base64.b64encode(buf.read()).decode('ascii')

        # Create an image tag for the heatmap
        return html.Img(src='data:image/png;base64,{}'.format(encoded_image), style={'width': '100%', 'height': 'auto'})

    elif pick_tab == 'pie':
            pie_data = merged_df1['name'].value_counts().reset_index()
            pie_data.columns = ['name', 'count']
            
            pie_fig = px.pie(pie_data, values='count', names='name',
                     title="Count of Threat Actors")
            
    return dcc.Graph(id='pie-graph', figure=pie_fig)


# Callback for dropdown selection 
@app.callback(
    Output('threat-details', 'children'),
    [Input('threat-dropdown-menu', 'value')]
)
def change_threat_details(pick_threat):
    if pick_threat:
        # Filter details for the selected threat_actor
        details = merged_df1[merged_df1['name'] == pick_threat].to_dict('records')[0]
        return html.Div([
            html.H4(f"Details for {pick_threat}"),
            html.P(f"Complexity Score: {details['complexity_score']}"),
            html.P(f"Prevalence Score: {details['prevalence_score']}")
        ])
    else:
        return "Select a threat actor to see details."

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
