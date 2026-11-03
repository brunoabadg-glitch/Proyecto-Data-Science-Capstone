# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the launch data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),

    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [
            {'label': site, 'value': site}
            for site in spacex_df['Launch Site'].unique()
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True,
        clearable=False
    ),
    html.Br(),

    # TASK 2: Successful launches by site, or outcomes for a selected site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P('Payload range (Kg):'),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={value: str(value) for value in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Relationship between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# TASK 2: Render the pie chart based on the selected launch site
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # class is binary: summing it counts successful launches only.
        success_counts = spacex_df.groupby('Launch Site', as_index=False)['class'].sum()
        fig = px.pie(
            success_counts,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = (
            filtered_df['class'].value_counts()
            .reindex([0, 1], fill_value=0)
            .rename_axis('class')
            .reset_index(name='Count')
        )
        outcome_counts['Outcome'] = outcome_counts['class'].map(
            {0: 'Failed', 1: 'Success'}
        )
        fig = px.pie(
            outcome_counts,
            values='Count',
            names='Outcome',
            title=f'Launch Outcomes for {entered_site}',
            color='Outcome',
            color_discrete_map={'Failed': '#EF553B', 'Success': '#00CC96'}
        )
    return fig


# TASK 4: Render the scatter chart based on site and payload range
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        spacex_df['Payload Mass (kg)'].between(low, high)
    ]

    if entered_site == 'ALL':
        title = 'Payload and Launch Outcome for All Sites'
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        title = f'Payload and Launch Outcome for {entered_site}'

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=title,
        labels={'class': 'Launch Outcome'}
    )
    fig.update_yaxes(tickvals=[0, 1], ticktext=['Failed (0)', 'Success (1)'])
    return fig


# Run the app
if __name__ == '__main__':
    app.run()

