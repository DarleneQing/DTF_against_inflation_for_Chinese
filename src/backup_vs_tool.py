from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, HoverTool, FactorRange, NumeralTickFormatter, Select, Div
from bokeh.layouts import column, row
from bokeh.models.annotations import Label
from bokeh.palettes import d3, tol

import pandas as pd
import numpy as np

# read all the pickle data files
df_asset = pd.read_pickle("data/asset_subset.pkl")
df_inflation = pd.read_pickle("data/inflation_subset.pkl")
pct_asset = pd.read_pickle("data/pct_asset.pkl")
pct_inflation = pd.read_pickle("data/pct_inflation.pkl")
data = pd.read_pickle("data/data_only.pkl")

# original data line chart
# Full palette
full_palette = list(d3['Category20'][16])

# Divide the palette into four segments
palette_segment_size = len(full_palette) // 4
palettes = [full_palette[i:i + palette_segment_size] for i in range(0, len(full_palette), palette_segment_size)]

# Assign each segment to a figure
p1_colors = palettes[0]
p2_colors = palettes[1]
p3_colors = palettes[2]
p4_colors = palettes[3]

# Initialize four figures and connect the x axises
p1 = figure(width=600, height=400, x_axis_type="datetime", title="Asset Prices 1")
p2 = figure(width=600, height=400, x_axis_type="datetime", title="Asset Prices 2", x_range=p1.x_range)
p3 = figure(width=600, height=400, x_axis_type="datetime", title="Inflation", x_range=p1.x_range)
p4 = figure(width=600, height=400, x_axis_type="datetime", title="CPI", x_range=p1.x_range)

# Add lines for assets
for i, col in enumerate(['House_price', 'Shanghai_stock_index', 'Gold_price', 'Fixed_deposit_rate']):
    source = ColumnDataSource(data={
        'x': df_asset['Time'],
        'y': df_asset[col],
        'label': [col] * len(df_asset)  # Repeat the column name to match the length of the data
    })
    p1.line('x', 'y', source=source, color=p1_colors[i % len(p1_colors)], legend_label=col)

for i, col in enumerate(['government_bond_yield_sixm', 'government_bond_yield_fivey', 'government_bond_yield_teny']):
    source = ColumnDataSource(data={
        'x': df_asset['Time'],
        'y': df_asset[col],
        'label': [col] * len(df_asset)  # Repeat the column name to match the length of the data
    })
    p2.line('x', 'y', source=source, color=p2_colors[i % len(p2_colors)], legend_label=col)

# Add lines for inflation indicators
for i, col in enumerate(['core_inflation', 'headline_inflation']):
    source = ColumnDataSource(data={
        'x': df_inflation['Time'],
        'y': df_inflation[col],
        'label': [col] * len(df_inflation)  # Repeat the column name to match the length of the data
    })
    p3.line('x', 'y', source=source, color=p3_colors[i + 1 % len(p3_colors)], legend_label=col)

for i, col in enumerate(['core_CPI', 'headline_CPI']):
    source = ColumnDataSource(data={
        'x': df_inflation['Time'],
        'y': df_inflation[col],
        'label': [col] * len(df_inflation)  # Repeat the column name to match the length of the data
    })
    p4.line('x', 'y', source=source, color=p4_colors[i % len(p4_colors)], legend_label=col)

# Add HoverTool
hover = HoverTool(tooltips=[("Label", "@label"), ("Time", "@x{%F}"), ("Value", "@y")], formatters={'@x': 'datetime'})
p1.add_tools(hover)
p2.add_tools(hover)
p3.add_tools(hover)
p4.add_tools(hover)

# Adjust the legends
p1.legend.location = "top_right"
p3.legend.location = "top_center"
p4.legend.location = "top_left"
p1.legend.background_fill_alpha = 0
p2.legend.background_fill_alpha = 0
p3.legend.background_fill_alpha = 0
p4.legend.background_fill_alpha = 0
p1.legend.label_text_font_size = "8pt"
p2.legend.label_text_font_size = "8pt"
p3.legend.label_text_font_size = "8pt"
p4.legend.label_text_font_size = "8pt"

# Give a markup instruction
instruction = Div(text="""
    <p style='background-color: #ADD8E6; padding: 10px; font-size: 16px;'><b>Instructions:</b> Hover over the plot to see data values. Use the toolbar to pan, zoom, and reset.<br>The four charts are connected, zoom in on one, the others will adjust accordingly.</p>
""", width=800, align="center", margin=10, )

# Layout
layout1 = column(instruction, row(p1, p2), row(p3, p4))

# percentage change in all assets and inflation indicators
years = sorted(df_asset['Year'].unique().tolist())
quarters = sorted(df_asset['Quarter'].unique().tolist())

select_pct_tag = 'All asset'
select_inflation_tag = 'All inflation'
asset_pct = pct_asset.drop(columns=['Time', 'Year', 'Quarter']).columns.tolist()
inflation_pct = pct_inflation.drop(columns=['Time', 'Year', 'Quarter']).columns.tolist()

palette = list(tol['TolRainbow'][14])
all_labels = sorted(set(inflation_pct) | set(asset_pct))
color_mapping = {label: palette[i % len(palette)] for i, label in enumerate(all_labels)}


def data_prepare_asset(select_tag):
    asset = []
    if select_tag == 'All asset':
        asset = asset_pct
    else:
        asset = [select_tag]
    data = pct_asset.pivot_table(
        values=asset,
        index=['Year', 'Quarter']
    )

    x_range = FactorRange(
        factors=[(str(year), quarter, item) for year in years for quarter in quarters for item in asset])

    x_labels = [(str(year), quarter, item) for year in years for quarter in quarters for item in asset]

    return data, x_labels, x_range


def data_prepare_inflation(select_tag):
    asset = []
    if select_tag == 'All inflation':
        asset = inflation_pct
    else:
        asset = [select_tag]
    data = pct_inflation.pivot_table(
        values=asset,
        index=['Year', 'Quarter']
    )

    x_range = FactorRange(
        factors=[(str(year), quarter, item) for year in years for quarter in quarters for item in asset])

    x_labels = [(str(year), quarter, item) for year in years for quarter in quarters for item in asset]

    return data, x_labels, x_range


def create_source(data, x_labels):
    y = data.values.flatten().tolist()

    labels = data.columns.tolist() * len(data)

    colors = [color_mapping[label] for label in labels]

    source = dict(
        x_labels=x_labels,
        y=y,
        label=labels,
        colors=colors,
        Year=[label[0] for label in x_labels],
        Quarter=[label[1] for label in x_labels]
    )

    return ColumnDataSource(source)


def draw_bar_chart(source, x_range):
    p = figure(

        x_range=x_range,
        title='Percentage Change',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width=1400,
        height=750
    )

    p.xgrid.grid_line_color = None

    p.x_range.range_padding = 0.1

    p.xaxis.major_label_text_font_size = '0px'

    p.xaxis.major_tick_line_color = None

    p.xaxis.axis_label = 'Datetime in year and quarter'

    p.yaxis.axis_label = 'Percentage Change (%)'

    p.yaxis.formatter = NumeralTickFormatter(format='0,0')

    p.vbar(
        x='x_labels',
        top='y',
        width=0.9,
        source=source,

        legend_group='label',
        line_color=None,

        fill_color='colors'
    )

    p.add_tools(HoverTool(tooltips=[
        ('Year', '@Year'),
        ('Quarter', '@Quarter'),
        ('Asset', '@label'),
        ('pct value', '@y{0,0.00}')
    ]))

    p.legend.label_text_font_size = '8pt'
    p.legend.label_height = 15
    p.legend.glyph_height = 10
    p.legend.glyph_width = 10
    p.legend.orientation = 'vertical'
    p.legend.location = 'top_right'
    p.legend.background_fill_alpha = 0

    p.output_backend = "svg"

    return p


def draw_line_chart(tag):
    p = figure(
        title='Percentage Change in line charts',
        tools='pan,wheel_zoom,box_zoom,reset,save',
        width=1400,
        height=750
    )

    p.xgrid.grid_line_color = None
    p.x_range.range_padding = 0.1
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Percentage Change (%)'

    p.yaxis.formatter = NumeralTickFormatter(format='0,0')

    data = pd.DataFrame()
    columns = []
    if tag == 'All assets in lines':
        data = pct_asset.drop(columns=['Year', 'Quarter']).copy()
        columns = asset_pct
    if tag == 'All inflations in lines':
        data = pct_inflation.drop(columns=['Year', 'Quarter']).copy()
        columns = inflation_pct

    palettes = list(tol['Bright'][7])

    for i, col in enumerate(columns):
        source = ColumnDataSource(data={
            'x': data['Time'],
            'y': data[col],
            'label': [col] * len(data)
        })

        p.line('x', 'y', source=source, color=palettes[i % len(palettes)], legend_label=col, line_width=1.5)

    p.add_tools(HoverTool(tooltips=[
        ('Asset', '@label'),
        ('Time', '@x{%F}'),
        ('percentage', '@y{0,0.00}')
    ], formatters={'@x': 'datetime'}))

    p.legend.background_fill_alpha = 0
    p.legend.label_text_font_size = "8pt"
    # p.legend.location = "top_center"

    return p


data, x_labels, x_range = data_prepare_asset(select_pct_tag)
source = create_source(data, x_labels)
data2, x_labels2, x_range2 = data_prepare_inflation(select_inflation_tag)
source2 = create_source(data2, x_labels2)

p = draw_bar_chart(source, x_range)
h = draw_bar_chart(source2, x_range2)

select_opt = ['All asset', 'All assets in lines'] + asset_pct
inflation_opt = ['All inflation', 'All inflations in lines'] + inflation_pct
select_asset = Select(title="Select Asset:", value=select_opt[0], options=select_opt)
select_inflation = Select(title="Select Inflation:", value=inflation_opt[0], options=inflation_opt)

layout2 = column(column(select_asset), column(p))
layout3 = column(column(select_inflation), column(h))


def update_asset_chart(attr, old, new):
    # global select_pct_tag, source
    select_pct_tag = new
    if new == 'All assets in lines':
        layout2.children[1].children[0] = draw_line_chart(new)
    else:
        data, labels, range = data_prepare_asset(select_pct_tag)
        source = create_source(data, labels)
        layout2.children[1].children[0] = draw_bar_chart(source, range)


def update_inflation_chart(attr, old, new):
    # global select_inflation_tag, source2
    select_inflation_tag = new
    if new == 'All inflations in lines':
        layout3.children[1].children[0] = draw_line_chart(new)
    else:
        data2, labels2, range2 = data_prepare_inflation(select_inflation_tag)
        source2 = create_source(data2, labels2)
        layout3.children[1].children[0] = draw_bar_chart(source2, range2)


select_asset.on_change('value', update_asset_chart)
select_inflation.on_change('value', update_inflation_chart)

div1 = Div(text="""
    <p style='background-color: #808080; padding: 10px; font-size: 24px;'><b>Figure I:</b> Original Value Over Time</p>
""", width=1000, align="center", margin=15, )

div2 = Div(text="""
    <p style='background-color: #808080; padding: 10px; font-size: 24px;'><b>Figure II:</b> Percentage Change Interaction</p>
""", width=1000, align="center", margin=15, )

div3 = Div(text="""
    <p style='background-color: #808080; padding: 10px; font-size: 24px;'><b>Figure III:</b> Proportion of Assets vs. Inflation Over Time Interaction</p>
""", width=1000, align="center", margin=15, )


def create_source_proportion(order_tag, asset_tag, inflation_tag):
    if order_tag == 'First Order':
        merged_df = pd.merge(df_asset, df_inflation.drop(columns=['Time']), on=['Year', 'Quarter'], how='inner')
        merged_df['Datetime'] = merged_df['Year'].astype(str) + merged_df['Quarter']
        merged_df.columns = ['Time', 'House_Change', 'Gold_Change', 'Fixed_deposit_Change', 'Shanghai_stock_Change',
                             'Gover_sixm_Change', 'Gover_fivey_Change', 'Gover_teny_Change', 'Year', 'Quarter',
                             'Core_CPI_Change','Headline_CPI_Change','Core_inflation_Change','Headline_inflation_Change', 'Datetime']
        inf = merged_df[inflation_tag]
        datas = []

        if asset_tag == "ALL":
            for i, asset in enumerate(asset_pct):
                prop = merged_df[[asset, 'Datetime']].copy()
                prop['Proportion'] = prop[asset] / inf
                prop = prop.drop(columns=[asset])
                prop['text'] = 'The proportion of all assets vs. '  + inflation_tag
                prop['label'] = asset
                datas.append(ColumnDataSource(prop))
        else:
            merged_df['Proportion'] = merged_df[asset_tag] / merged_df[inflation_tag].replace({0: np.nan})
            data = merged_df[['Datetime', 'Proportion']].copy()
            data['text'] = 'The proportion of ' + asset_tag + ' and ' + inflation_tag
            data['label'] = asset_tag
            datas.append(ColumnDataSource(data))

    if order_tag == 'Second Order':
        merged_df2 = pd.merge(pct_asset, pct_inflation.drop(columns=['Time']), on=['Year', 'Quarter'], how='inner')
        merged_df2['Datetime'] = merged_df2['Year'].astype(str) + merged_df2['Quarter']
        inf = merged_df2[inflation_tag]
        datas = []

        if asset_tag == "ALL":
            for i, asset in enumerate(asset_pct):
                prop = merged_df2[[asset, 'Datetime']].copy()
                prop['Proportion'] = prop[asset] / inf
                prop = prop.drop(columns=[asset])
                prop['text'] = 'The proportion of all assets vs. '  + inflation_tag
                prop['label'] = asset
                datas.append(ColumnDataSource(prop))
        else:
            merged_df2['Proportion'] = merged_df2[asset_tag] / merged_df2[inflation_tag].replace({0: np.nan})
            data = merged_df2[['Datetime', 'Proportion']].copy()
            data['text'] = 'The proportion of ' + asset_tag + ' and ' + inflation_tag
            data['label'] = asset_tag
            datas.append(ColumnDataSource(data))

    return datas


def draw_line_chart_prop(source_prop):
    p = figure(
        width=1400,
        height=750,
        title='Proportion of Assets vs. Inflation Indicators',
        x_range=source_prop[0].data['Datetime'],
        tools="pan,wheel_zoom,box_zoom,reset,save",
        toolbar_location='right'
    )

    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = 'vertical'

    palettes = list(tol['Light'][7])

    for i, src in enumerate(source_prop):
        p.line(
            x='Datetime',
            y='Proportion',
            source=src,
            color=palettes[i % len(palettes)],
            legend_label=src.data['label'][0],
            line_width=1.5
        )

        label = Label(
            x=700,
            y=650,
            x_units='screen',
            y_units='screen',
            text=src.data['text'][0],
            text_font_size='10pt',
            text_font_style='bold',
            text_color='black',
            text_align='center'
        )

    p.add_tools(HoverTool(tooltips=[('Label', '@label'), ('Time', '@Datetime'), ('Proportion', '@Proportion')]))

    p.xaxis.axis_label = 'Datetime'
    p.yaxis.axis_label = 'Proportion'
    p.legend.label_text_font_size = "8pt"
    p.legend.location = "bottom_left"
    p.legend.background_fill_alpha = 0

    p.add_layout(label)

    p.output_backend = 'svg'

    return p


order_tag = 'First Order'
asset_tag = 'ALL'
inflation_tag = 'Core_CPI_Change'

_source = create_source_proportion(order_tag, asset_tag, inflation_tag)

m = draw_line_chart_prop(_source)

select_order = Select(title="Select Order:", value="First Order", options=["First Order", "Second Order"])
select_asset2 = Select(title="Select Asset:", value="ALL", options=asset_pct + ["ALL"])
select_inflation2 = Select(title="Select Inflation:", value=inflation_pct[0], options=inflation_pct)

layout4 = row(select_order, select_asset2, select_inflation2)
layout5 = row(m)


def update_order(attr, old, new):
    order_tag = new
    source = create_source_proportion(order_tag, asset_tag, inflation_tag)
    layout5.children[0] = draw_line_chart_prop(source)

def update_asset(attr, old, new):
    asset_tag = new
    _source = create_source_proportion(order_tag, asset_tag, inflation_tag)
    layout5.children[0] = draw_line_chart_prop(_source)


def update_inflation(attr, old, new):
    inflation_tag = new
    _source = create_source_proportion(order_tag, asset_tag, inflation_tag)
    layout5.children[0] = draw_line_chart_prop(_source)


select_order.on_change('value', update_order)
select_asset2.on_change('value', update_asset)
select_inflation2.on_change('value', update_inflation)

# Combine all figure into one layout
layout = column(div1, layout1, div2, layout2, layout3, div3, layout4, layout5)

curdoc().add_root(layout)
