import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import requests
from io import BytesIO
import os

# URL direta para a imagem no GitHub
image_url = 'https://github.com/JacoLucas/EstoqueIIPG/raw/main/LOGO MLC Infra.jpg'

# URLs das planilhas no GitHub (substituindo espaços por %20)
url_base = 'https://github.com/JacoLucas/EstoqueIIPG/raw/main/Long_Estoque IIPG.xlsx'

def carregar_planilha(url, sheet_name):
    response = requests.get(url)
    if response.status_code == 200:
        df = pd.read_excel(BytesIO(response.content), sheet_name=sheet_name, engine='openpyxl')
        return df
    else:
        raise Exception("Falha ao baixar o arquivo do GitHub. Verifique a URL e tente novamente.")

# Carregando os dados das planilhas
df1 = carregar_planilha(url_base, 'PRIMARIO')
df2 = carregar_planilha(url_base, 'SECUNDARIO')
df_usauss = carregar_planilha(url_base, 'USA&USS')
df1 = df1.fillna(0)
df2 = df2.fillna(0)
df_usauss = df_usauss.fillna(0)

df1.rename(columns={
    'Estoque RD': 'Rocha Detonada',
    'Estoque Rachão': 'Rachão'
}, inplace=True)

df1['Dias'] = pd.to_datetime(df1['Dias'], format='%d/%m/%Y')
df2['Dias'] = pd.to_datetime(df2['Dias'], format='%d/%m/%Y')
df_usauss['Dias'] = pd.to_datetime(df_usauss['Dias'], format='%d/%m/%Y')

# Criando uma coluna 'Mês' no formato 'YYYY-MM'
df1['Mês'] = df1['Dias'].dt.to_period('M')
df2['Mês'] = df2['Dias'].dt.to_period('M')
df_usauss['Mês'] = df_usauss['Dias'].dt.to_period('M')

# Inicializando o app Dash
app = dash.Dash(__name__)
app.title = 'Estoque IIPG'

# Layout do aplicativo
app.layout = html.Div([
    html.Img(src= image_url, 
             style={'position': 'absolute', 'top': '10px', 'right': '10px', 'width': '220px', 'height': '180px'}),

    html.H1('Estoque de Materiais Inst. Ind. Ponta Grossa - IIPG'),
    
    ######### ATUALIZAR SEMPRE #########
    html.H3('Atualizado dia 28/01/25 - 16:30 - Fase de testes, valores apenas para exemplo'), 
    ######### ATUALIZAR SEMPRE #########
    
    html.Div([
    html.Label('Selecione o Período:'),
    dcc.Dropdown(
        id='month-dropdown',
        options=[{'label': str(month), 'value': str(month)} for month in df1['Mês'].unique()],
        value=str(df1['Mês'].unique()[0])
    )], style= {'width': '33%', 'display': 'inline-block', 'margin-bottom': '20px'}),
    
html.Div([
    html.H2('Sistema Primário - Britagem'),
    dcc.Graph(id='line1-graph', style={'width': '70%', 'display': 'inline-block'}),
    dcc.Graph(id='pie1-graph', style={'width': '30%', 'display': 'inline-block'})
    ]),
html.Div([
    html.H2('Sistema Secundário - Rebritagem'),
    dcc.Graph(id='line2-graph', style={'width': '70%', 'display': 'inline-block'}),
    dcc.Graph(id='pie2-graph', style={'width': '30%', 'display': 'inline-block'}),
    ]),
html.Div([
    dcc.Graph(id='bar1-graph', style={'width': '70%', 'display': 'inline-block'}),
    html.Div(id='table-div', style={'width': '30%', 'display': 'inline-block', 'vertical-align': 'middle', 'margin-left': 'auto', 'margin-right': '0%', 'text-align': 'center'})
], style={'display': 'flex', 'align-items': 'center'}
    ),
html.Div([
    html.H2('Produção USA e USS'),
    html.Div([
        html.Label('Selecione a Usina:'),
        dcc.Dropdown(
            id='unit-dropdown',
            options=[
                {'label': 'USA', 'value': 'USA'},
                {'label': 'USS', 'value': 'USS'}
            ],
            value='USA',
            clearable=False
        )
    ], style={'width': '33%', 'margin-bottom': '20px'}),
    dcc.Graph(id='usa-uss-graph', style={'width': '95%', 'display': 'inline-block'}),
    html.Div(id='usa-uss-pie-graphs', style={'width': '100%', 'display': 'inline-block'})
    ], style={'margin-top': '20px'})
])
# Callback para atualizar o gráfico com base no mês selecionado
@app.callback(
    [Output('line1-graph', 'figure'),
    Output('pie1-graph', 'figure'),
    Output('line2-graph', 'figure'),
    Output('pie2-graph', 'figure'),
    Output('bar1-graph', 'figure'),
    Output('table-div', 'children'),
    Output('usa-uss-graph', 'figure'),
    Output('usa-uss-pie-graphs', 'children')],
    [Input('month-dropdown', 'value'),
     Input('unit-dropdown', 'value')]
)

def update_graph(selected_month, selected_unit):

    # DEFINIÇÃO DE CORES #

    color_line1 = {'Rocha Detonada': '#006699', 
               'Rachão': '#990033'}

    color_pie1 = {'Vendas': '#006699', 
                  'Obras': '#660099', 
                  'Estoque': '#990033'}

    color_line2 = {'Macadame': '#3399FF',
            'Pó de Pedra': '#006699',
            'Pedrisco': '#660099',
            'Brita 1': '#990033',
            'Brita 2': '#FFCC00'}

    color_pie2 = {'Pó de Pedra': '#006699',
            'Pedrisco': '#660099',
            'Brita 1': '#990033',
            'Brita 2': '#FFCC00'}

    color_bar1 = {'Vendas': '#990033', 
                  'Obras': '#006699'}

    color_fig_USA = {'Cimento Asfáltico': '#339966',
            'Pó de Pedra': '#006699',
            'Pedrisco': '#660099',
            'Brita 1': '#990033',
            'Brita 2': '#FFCC00',
            'Enchimento': '#CC0099'}

    color_fig_USS = {'Pó de Pedra': '#006699',
            'Pedrisco': '#660099',
            'Brita 1': '#990033',
            'Brita 2': '#FFCC00',
            'Cimento': '#CC0066'}

    color_pie_cbuq = {'Vendas CBUQ': '#990033', 
                'Obras CBUQ': '#006699'}
    color_pie_binder = {'Vendas Binder': '#990033', 
                'Obras Binder': '#006699'}
    color_pie_bgs = {'Vendas BGS': '#990033', 
                'Obras BGS': '#006699'}
    color_pie_bgmc = {'Vendas BGMC': '#990033', 
                'Obras BGMC': '#006699'}
    color_pie_bgtc = {'Vendas BGTC': '#990033', 
                'Obras BGTC': '#006699'}

    # SISTEMA PRIMÁRIO #

    filtered_data1 = df1[df1['Mês'] == selected_month]

    fig_line1 = px.line(filtered_data1, 
                  x='Dias', 
                  y=['Rocha Detonada', 'Rachão'],
                  labels={'value': 'Estoque (ton.)', 'variable': 'Material'},
                  title=f'Estoque - {selected_month}',
                  color_discrete_map=color_line1
                  )
    # Adicionando scatter plot para os pontos onde Obs != 0
    scatter_points = go.Scatter(
        x=filtered_data1[filtered_data1['Obs'] != 0]['Dias'],
        y=[0] * len(filtered_data1[filtered_data1['Obs'] != 0]),
        mode='markers',
        name='Observação',
        marker=dict(color='red', size=10),
        text=filtered_data1[filtered_data1['Obs'] != 0]['Obs'],
        textposition='top center',
        hovertext=filtered_data1[filtered_data1['Obs'] != 0]['Obs']
    )

    # Atualizando o layout do gráfico
    fig_line1.add_trace(scatter_points)
    fig_line1.update_layout(
        xaxis_title=f'{selected_month}',
        xaxis=dict(
            tickmode='linear',
            dtick='D1',
            tickformat='%d'
        ),
        yaxis=dict(
            range=[0,max(filtered_data1[['Rocha Detonada', 'Rachão']].max()) + 5]
        )
    )
    
    # Calculando as porcentagens para o gráfico de pizza
    total_producao = filtered_data1['Total Producao'].sum()
    vendas_total = filtered_data1['Vendas'].sum()
    obras_total = filtered_data1['Obras'].sum()
    estoque_total = total_producao - (vendas_total + obras_total)

    pie_data = pd.DataFrame({
        'Categoria': ['Vendas', 'Obras', 'Estoque'],
        'Quantidade': [vendas_total, obras_total, estoque_total]
    })
    
    # Gráfico de pizza
    fig_pie1 = px.pie(pie_data, values='Quantidade', names='Categoria',
                     title=f'Distribuição de Saída de Materiais - {selected_month}',
                     labels={'Quantidade': 'Quantidade', 'Categoria': 'Categoria'},
                     color= 'Categoria',
                     color_discrete_map=color_pie1)
    
    # SISTEMA SECUNDÁRIO #

    df2.rename(columns= {
               'Estoque Mac': 'Macadame',
               'Estoque Po': 'Pó de Pedra',
               'Estoque Ped': 'Pedrisco',
               'Estoque B1': 'Brita 1',
               'Estoque B2': 'Brita 2'}, inplace= True)

    filtered_data2 = df2[df2['Mês'] == selected_month]
    
    fig_line2 = px.line(filtered_data2, 
                  x='Dias', 
                  y=['Macadame', 'Pó de Pedra', 'Pedrisco', 'Brita 1', 'Brita 2'],
                  labels={'value': 'Estoque (ton.)', 'variable': 'Material'},
                  title=f'Estoque de Materiais - {selected_month}',
                  color_discrete_map=color_line2
                  )
    # Adicionando scatter plot para os pontos onde Obs != 0
    scatter_points = go.Scatter(
        x=filtered_data2[filtered_data2['Obs'] != 0]['Dias'],
        y=[0] * len(filtered_data2[filtered_data2['Obs'] != 0]),
        mode='markers',
        name='Observação',
        marker=dict(color='red', size=10),
        text=filtered_data2[filtered_data2['Obs'] != 0]['Obs'],
        textposition='top center',
        hovertext=filtered_data2[filtered_data2['Obs'] != 0]['Obs']
    )

    # Atualizando o layout do gráfico
    fig_line2.add_trace(scatter_points)
    fig_line2.update_layout(
        xaxis_title=f'{selected_month}',
        xaxis=dict(
            tickmode='linear',
            dtick='D1',
            tickformat='%d'
        ),
        yaxis=dict(
            range=[0, max(filtered_data2[['Macadame', 'Pó de Pedra', 'Pedrisco', 'Brita 1', 'Brita 2']].max()) + 5]
        )
    )

    macadame = filtered_data2['Macadame'].sum()
    podepedra = filtered_data2['Pó de Pedra'].sum()
    pedrisco = filtered_data2['Pedrisco'].sum()
    brita1 = filtered_data2['Brita 1'].sum()
    brita2 = filtered_data2['Brita 2'].sum()

    pie2_data = pd.DataFrame({
        'Materiais': ['Macadame', 'Pó de Pedra', 'Pedrisco', 'Brita 1', 'Brita 2'],
        'Quantidades': [macadame, podepedra, pedrisco, brita1, brita2]
    })

    fig_pie2 = px.pie(pie2_data, values='Quantidades', names='Materiais',
                     title=f'Distribuição de Materiais no Estoque - {selected_month}',
                     labels={'Quantidade': 'Quantidade', 'Materiais': 'Materiais'},
                     color= 'Materiais',
                     color_discrete_map= color_pie2)

    # Gráfico de barras
    bar1_data = {
        'Material': ['Macadame', 'Macadame', 'Pó de Pedra', 'Pó de Pedra', 'Pedrisco', 'Pedrisco', 'Brita 1', 'Brita 1', 'Brita 2', 'Brita 2'],
        'Categoria': ['Vendas', 'Obras', 'Vendas', 'Obras', 'Vendas', 'Obras', 'Vendas', 'Obras', 'Vendas', 'Obras'],
        'Quantidade': [
            filtered_data2['Venda Mac'].sum(), filtered_data2['Obras Mac'].sum(),
            filtered_data2['Venda Po'].sum(), filtered_data2['Obras Po'].sum(),
            filtered_data2['Venda Ped'].sum(), filtered_data2['Obras Ped'].sum(),
            filtered_data2['Venda B1'].sum(), filtered_data2['Obras B1'].sum(),
            filtered_data2['Venda B2'].sum(), filtered_data2['Obras B2'].sum()
        ]
    }
    bar1_df = pd.DataFrame(bar1_data)
    bar1_fig = px.bar(bar1_df, x='Material', y='Quantidade', color='Categoria', barmode='group',
                     title=f'Saídas Totais de Materiais - {selected_month}',
                     labels={'Quantidade': 'Quantidade (ton.)'},
                     color_discrete_map=color_bar1)

    # Tabela
    table = html.Table([
        html.Thead(
            html.Tr([html.Th("Material"), html.Th("Vendas (ton.)"), html.Th("Obras (ton.)")])
        ),
        html.Tbody([
            html.Tr([html.Td("Macadame"), html.Td(filtered_data2['Venda Mac'].sum()), html.Td(filtered_data2['Obras Mac'].sum())]),
            html.Tr([html.Td("Pó de Pedra"), html.Td(filtered_data2['Venda Po'].sum()), html.Td(filtered_data2['Obras Po'].sum())]),
            html.Tr([html.Td("Pedrisco"), html.Td(filtered_data2['Venda Ped'].sum()), html.Td(filtered_data2['Obras Ped'].sum())]),
            html.Tr([html.Td("Brita 1"), html.Td(filtered_data2['Venda B1'].sum()), html.Td(filtered_data2['Obras B1'].sum())]),
            html.Tr([html.Td("Brita 2"), html.Td(filtered_data2['Venda B2'].sum()), html.Td(filtered_data2['Obras B2'].sum())])
        ])
    ], style={'border': '2px solid black', 'border-collapse': 'collapse', 'width': '100%', 'text-align': 'center'})

    # Adicionando bordas às células da tabela
    for elem in table.children:
        for row in elem.children:
            for cell in row.children:
                cell.style = {'border': '1px solid black', 'padding': '8px'}

    # USA & USS #

    # Filtrando df_usauss por mês selecionado
    filtered_df_usauss = df_usauss[df_usauss['Mês'] == selected_month]

    # Separando dados da USA e USS
    df_usa = filtered_df_usauss.drop(columns={'BGS', 'Vendas BGS', 'Obras BGS', 
                                              'BGMC', 'Vendas BGMC', 'Obras BGMC', 
                                              'BGTC', 'Vendas BGTC', 'Obras BGTC',
                                              'USS Cimento', 'USS B2', 'USS B1', 'USS Pedrisco', 'USS Pó de Pedra'
                                              })
    df_usa.rename(columns={'USA B2': 'Brita 2',
                           'USA B1': 'Brita 1',
                           'USA Pedrisco': 'Pedrisco',
                           'USA Pó de Pedra': 'Pó de Pedra'}, inplace=True)

    df_uss = filtered_df_usauss.drop(columns={'USA B2', 'USA B1', 'USA Pedrisco', 'USA Pó de Pedra', 'Enchimento',
                                              'CBUQ', 'Vendas CBUQ', 'Obras CBUQ', 
                                              'Binder', 'Vendas Binder', 'Obras Binder',
                                              'Cimento Asfáltico'})
    df_uss.rename(columns={'USS B2': 'Brita 2',
                           'USS B1': 'Brita 1',
                           'USS Pedrisco': 'Pedrisco',
                           'USS Pó de Pedra': 'Pó de Pedra',
                           'USS Cimento': 'Cimento'}, inplace=True)

    # DataFrames para USA pie
    usa_cbuq_pie = df_usa[['Vendas CBUQ', 'Obras CBUQ']].sum().reset_index()
    usa_cbuq_pie.columns = ['Categoria', 'Quantidade']

    usa_binder_pie = df_usa[['Vendas Binder', 'Obras Binder']].sum().reset_index()
    usa_binder_pie.columns = ['Categoria', 'Quantidade']

    # DataFrames para USS pie
    uss_bgs_pie = df_uss[['Vendas BGS', 'Obras BGS']].sum().reset_index()
    uss_bgs_pie.columns = ['Categoria', 'Quantidade']

    uss_bgmc_pie = df_uss[['Vendas BGMC', 'Obras BGMC']].sum().reset_index()
    uss_bgmc_pie.columns = ['Categoria', 'Quantidade']
  
    uss_bgtc_pie = df_uss[['Vendas BGTC', 'Obras BGTC']].sum().reset_index()
    uss_bgtc_pie.columns = ['Categoria', 'Quantidade']

    # Gráficos pie para USA
    fig_usa_cbuq_pie = px.pie(usa_cbuq_pie, values='Quantidade', names='Categoria',
                              title='Distribuição de CBUQ - USA',
                              color= 'Categoria',
                              color_discrete_map=color_pie_cbuq)

    fig_usa_binder_pie = px.pie(usa_binder_pie, values='Quantidade', names='Categoria',
                                title='Distribuição de Binder - USA',
                                color= 'Categoria',
                                color_discrete_map=color_pie_binder)

    # Gráficos pie para USS
    fig_uss_bgs_pie = px.pie(uss_bgs_pie, values='Quantidade', names='Categoria',
                             title='Distribuição de BGS - USS',
                             color= 'Categoria',
                             color_discrete_map=color_pie_bgs)

    fig_uss_bgmc_pie = px.pie(uss_bgmc_pie, values='Quantidade', names='Categoria',
                              title='Distribuição de BGMC - USS',
                              color= 'Categoria',
                              color_discrete_map=color_pie_bgmc)

    fig_uss_bgtc_pie = px.pie(uss_bgtc_pie, values='Quantidade', names='Categoria',
                              title='Distribuição de BGTC - USS',
                              color= 'Categoria',
                              color_discrete_map=color_pie_bgtc)


    # Configurando fig_USAUSS com base na unidade selecionada
    if selected_unit == 'USA':
        fig_USAUSS = px.line(df_usa,
                            x='Dias', 
                            y=['Cimento Asfáltico', 'Brita 2', 'Brita 1', 'Pedrisco', 'Pó de Pedra', 'Enchimento'],
                            labels={'value': 'Quantidade (ton.)', 'variable': 'Material'},
                            title=f'Entrada de Materiais USA - {selected_month}',
                            color_discrete_map=color_fig_USA
                            )
        # Adicionando scatter plot para os pontos onde Obs != 0
        scatter_points = go.Scatter(
            x=df_usa[df_usa['Obs'] != 0]['Dias'],
            y=[0] * len(df_usa[df_usa['Obs'] != 0]),
            mode='markers',
            name='Observação',
            marker=dict(color='red', size=10),
            text=df_usa[df_usa['Obs'] != 0]['Obs'],
            textposition='top center',
            hovertext=df_usa[df_usa['Obs'] != 0]['Obs']
        )

        # Atualizando o layout do gráfico
        fig_USAUSS.add_trace(scatter_points)
        fig_USAUSS.update_layout(
            xaxis_title=f'{selected_month}',
            xaxis=dict(
                tickmode='linear',
                dtick='D1',
                tickformat='%d'
            ),
            yaxis=dict(
                range=[0, max(df_usa[['Pó de Pedra', 'Pedrisco', 'Brita 1', 'Brita 2']].max()) + 5]
            )
        )

        pie_graphs = html.Div([
            dcc.Graph(figure=fig_usa_cbuq_pie, 
                      style={'width': '50%', 'display': 'inline-block'}
                      ),
            dcc.Graph(figure=fig_usa_binder_pie, 
                      style={'width': '50%', 'display': 'inline-block'}
                      )
        ])
        fig_usa_cbuq_pie.update_traces(labels=['Vendas', 'Consumo'])
        fig_usa_cbuq_pie.update_layout(title_x= 0.48)
        fig_usa_binder_pie.update_traces(labels=['Vendas', 'Consumo'])
        fig_usa_binder_pie.update_layout(title_x= 0.47)

    else:
        fig_USAUSS = px.line(df_uss,
                            x='Dias', 
                            y=['Brita 2', 'Brita 1', 'Pedrisco', 'Pó de Pedra', 'Cimento'],
                            labels={'value': 'Quantidade (ton.)', 'variable': 'Material'},
                            title=f'Entrada de Materiais USS - {selected_month}',
                            color_discrete_map=color_fig_USS
                            )
        # Adicionando scatter plot para os pontos onde Obs != 0
        scatter_points = go.Scatter(
            x=df_uss[df_uss['Obs'] != 0]['Dias'],
            y=[0] * len(df_uss[df_uss['Obs'] != 0]),
            mode='markers',
            name='Observação',
            marker=dict(color='red', size=10),
            text=df_uss[df_uss['Obs'] != 0]['Obs'],
            textposition='top center',
            hovertext=df_uss[df_uss['Obs'] != 0]['Obs']
        )

        # Atualizando o layout do gráfico
        fig_USAUSS.add_trace(scatter_points)
        fig_USAUSS.update_layout(
            xaxis_title=f'{selected_month}',
            xaxis=dict(
                tickmode='linear',
                dtick='D1',
                tickformat='%d'
            ),
            yaxis=dict(
                range=[0, max(df_uss[['Pó de Pedra', 'Pedrisco', 'Brita 1', 'Brita 2']].max()) + 5]
            )
        )
        pie_graphs = html.Div([
            dcc.Graph(figure=fig_uss_bgs_pie, 
                      style={'width': '33%', 'display': 'inline-block'}
                      ),
            dcc.Graph(figure=fig_uss_bgmc_pie, 
                      style={'width': '33%', 'display': 'inline-block'}
                      ),
            dcc.Graph(figure=fig_uss_bgtc_pie, 
                      style={'width': '33%', 'display': 'inline-block'}
                      )
        ])
        fig_uss_bgs_pie.update_traces(labels=['Vendas', 'Consumo'])
        fig_uss_bgs_pie.update_layout(title_x= 0.48)
        fig_uss_bgmc_pie.update_traces(labels=['Vendas', 'Consumo'])
        fig_uss_bgmc_pie.update_layout(title_x= 0.46)
        fig_uss_bgtc_pie.update_traces(labels=['Vendas', 'Consumo'])
        fig_uss_bgtc_pie.update_layout(title_x= 0.46)

    fig_USAUSS.update_layout(
        xaxis_title=f'{selected_month}',
        xaxis=dict(
            tickmode='linear',
            dtick='D1',
            tickformat='%d'
        ))
    

    return fig_line1, fig_pie1, fig_line2, fig_pie2, bar1_fig, table, fig_USAUSS, pie_graphs

# Rodando o aplicativo
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8050))
    app.run_server(debug=True, host='0.0.0.0', port=port)
    
