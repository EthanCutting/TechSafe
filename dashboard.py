# created by: Ethan PP Cutting (100942775)
# created date: 1/10/24
# last modified by: Ethan PP Cutting 
# modified date: 7/10/24

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
import os

# Loading the dataset 
data_path = 'C:/Users/ethan/Desktop/TechSafe-main/TechSafe-main/Dataset/merged_data.csv'

if not os.path.exists(data_path):
    raise FileNotFoundError(f"The file {data_path} does not exist.")
merged_df1 = pd.read_csv(data_path)

merged_df1['created_x'] = pd.to_datetime(merged_df1['created_x'], errors='coerce')
merged_df1['YearMonth'] = merged_df1['created_x'].dt.to_period('M')

# Group by YearMonth for activity plot
activity_counts = merged_df1.groupby(['YearMonth', 'name']).size().reset_index(name='Counts')
activity_pivot = activity_counts.pivot(index='YearMonth', columns='name', values='Counts')
unique_actors = activity_pivot.columns.tolist()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = html.Div(children=[
    # Logo section 
    html.Div([
        html.Img(src='/assets/techsafe-high-resolution-logo-transparent.png', 
                 style={'width': '500px', 'display': 'block', 'margin': 'auto'}),
    ], className='logo-container'),  
    
    # Pie Chart Section for Top Threat Actors
    html.Div([
        html.H2('Pie Chart'),
        dcc.Graph(id='top-threat-actors-pie'),
        
        # Year Dropdown for Pie Chart
        html.H2('Select Year for Top Threat Actors'),
        dcc.Dropdown(
            id='year-dropdown',  
            options=[{'label': str(year), 'value': year} for year in sorted(merged_df1['created_x'].dt.year.dropna().unique())],
            value=sorted(merged_df1['created_x'].dt.year.dropna().unique())[0],  
            placeholder='Select Year'
        ),
        html.P("Select a year to view the top 5 threat actors for that specific year."),  # Text description
    ], className='section-container'),  

   
    # Dropdown for the heatmap
    html.Div([
        # Heatmap container 
        html.Div(id='heatmap-container', className='section-container'), 
        html.H2('Select a Threat Actor for Heatmap'),
        dcc.Dropdown(
            id='threat-dropdown-menu',
            options=[{'label': threat, 'value': threat} for threat in merged_df1['name'].unique()],
            placeholder='Select a threat actor'
        ),
    ], className='section-container'),  

    # Threat Actor Activity Timeline section
    html.Div([
        html.H2('Timeline'),

        dcc.Graph(id='activity-graph'),
        html.H2('Select a Threat Actor for Timeline'),
        dcc.Dropdown(
            id='actor-activity-dropdown',
            options=[{'label': actor, 'value': actor} for actor in unique_actors],
            placeholder='Select a Threat Actor'
        ),
    ], className='section-container') 
])


# Callback for the heatmap 
@app.callback(
    Output('heatmap-container', 'children'),
    Input('threat-dropdown-menu', 'value')
)
def update_heatmap(pick_threat):
    df_filtered = merged_df1[['name', 'technique']].copy() 
    df_filtered['technique'] = df_filtered['technique'].str.split(',')
    df_exploded = df_filtered.explode('technique')
    heatmap_data = pd.crosstab(df_exploded['technique'], df_exploded['name'])

    heatmap_fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='YlGnBu',
        colorbar=dict(title='Count')
    ))

    annotations = []
    for i, row in enumerate(heatmap_data.index):
        for j, col in enumerate(heatmap_data.columns):
            value = heatmap_data.iloc[i, j]
            annotations.append(
                dict(
                    x=col,
                    y=row,
                    text=str(value),
                    showarrow=False,
                    font=dict(color='white')
                )
            )

    # Set the lighter background for the heatmap container
    heatmap_fig.update_layout(
        title='Technique Correlations',
        paper_bgcolor='#2e2e2e', 
        plot_bgcolor='#2e2e2e',   
        font_color='#e0e0e0',     
        title_font_color='#e0e0e0', 
        xaxis_title='Threat Actors',
        yaxis_title='Techniques',
        annotations=annotations,
        height=1500,
        width=1500,
        xaxis=dict(tickangle=-45, tickfont=dict(color='#e0e0e0')),
        yaxis=dict(tickfont=dict(color='#e0e0e0'))
    )
    return dcc.Graph(figure=heatmap_fig)


# Callback for the pie chart 
@app.callback(
    Output('top-threat-actors-pie', 'figure'),
    Input('year-dropdown', 'value')
)
def update_pie_chart(selected_year):
    merged_df1['Year'] = merged_df1['created_x'].dt.year
    yearly_actor_counts = merged_df1.groupby(['Year', 'name']).size().reset_index(name='Counts')
    top_n = 5
    top_actors = yearly_actor_counts.groupby('name').size().reset_index(name='Counts').nlargest(top_n, 'Counts')

    pie_fig = px.pie(top_actors, values='Counts', names='name',
                     title=f'Top {top_n} Threat Actors in {selected_year}',
                     hole=0.3)
     # Set the lighter background for the pie chart container
    pie_fig.update_layout(
        paper_bgcolor='#2e2e2e',  
        plot_bgcolor='#2e2e2e',   
        font_color='#e0e0e0',
        title_font_color='#e0e0e0',
        legend_bgcolor='#2e2e2e',
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
        margin=dict(l=20, r=20, t=40, b=20) 
    )
    return pie_fig

# Callback for timeline graph
@app.callback(
    Output('activity-graph', 'figure'),
    Input('actor-activity-dropdown', 'value')
)
def plot_activity(actor):
    if actor:
        actor_data = activity_pivot[actor]
        activity_fig = go.Figure()
        activity_fig.add_trace(go.Scatter(
            x=activity_pivot.index.astype(str),
            y=actor_data,
            mode='lines+markers',
            name=actor
        ))
        # Set the lighter background for the graph container
        activity_fig.update_layout(
            title=f'Timeline of {actor} Activity over time',
            xaxis_title='Time (Year-Month)',
            yaxis_title='Number of Incidents',
            paper_bgcolor='#2e2e2e',  
            plot_bgcolor='#2e2e2e',   
            font_color='#e0e0e0',     
            title_font_color='#e0e0e0',
            xaxis=dict(tickangle=45, tickfont=dict(color='#e0e0e0'), showgrid=False),
            yaxis=dict(tickfont=dict(color='#e0e0e0'), showgrid=False),
            margin=dict(l=20, r=20, t=40, b=20),  
        )
        return activity_fig
    return go.Figure()

if __name__ == '__main__':
    app.run_server(debug=True)
 
