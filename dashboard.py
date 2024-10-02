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

# Loading the dataset 
data_path = 'C:\\Users\\Owner\\Cos7008\\Merge_DataSet.csv'

if not os.path.exists(data_path):
    raise FileNotFoundError(f"The file {data_path} does not exist.")
merged_df1 = pd.read_csv(data_path)

# Print DataFrame for debugging
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
    
    # Bar Graph Section
    html.Div([
        html.H2('Bar Graph: Complexity Score by Threat Actor'),
        dcc.Graph(id='bar-graph'),
    ]),
    
    # Heatmap Section
    html.Div([
        html.H2('Heatmap: Technique Correlations'),
        html.Div(id='heatmap-container'),
    ]),
    
    # Pie Chart Section
    html.Div([
        html.H2('Pie Chart: Count of Threat Actors'),
        dcc.Graph(id='pie-graph'),
    ]),
])


# Callback to update bar graph
@app.callback(
    Output('bar-graph', 'figure'),
    Input('threat-dropdown-menu', 'value')
)
def update_bar_graph(pick_threat):
    # Placeholder bar graph (you can customize it with appropriate x, y values)
    bar_fig = px.bar(merged_df1, x='name', y='complexity_score',
                     title="Complexity Score by Threat Actor",
                     labels={'complexity_score': 'Complexity Score', 'name': 'Threat Actor'})
    return bar_fig


# Callback to generate heatmap image
@app.callback(
    Output('heatmap-container', 'children'),
    Input('threat-dropdown-menu', 'value')
)
def update_heatmap(pick_threat):
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

    # Return the image as a base64-encoded string
    return html.Img(src='data:image/png;base64,{}'.format(encoded_image), style={'width': '100%', 'height': 'auto'})


# Callback to update pie chart
@app.callback(
    Output('pie-graph', 'figure'),
    Input('threat-dropdown-menu', 'value')
)
def update_pie_chart(pick_threat):
    pie_data = merged_df1['name'].value_counts().reset_index()
    pie_data.columns = ['name', 'count']
    
    pie_fig = px.pie(pie_data, values='count', names='name',
                     title="Count of Threat Actors")
    return pie_fig


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
