#!/usr/bin/env python
# coding: utf-8

# # SMNA-Dashboard
#  
# Este notebook trata da apresentação do espaço utilizado pelos arquivos de observações disponíveis para a utilização com o SMNA. As informações apresentadas não representam quantidades ou tipos de dados envolvidos ou utiizados no processo de assimilação de dados, mas apenas o espaço em disco utilizado por estes. As informações mais importantes que podem ser obtidas com este dashboard são o espaço em disco total utilizado por diferentes tipos de observações, separadas por horário sinótico, período e tipo de dados.
#  
# **Nota:** Se o slider que permite ajustar o período a ser visualizado não atualizar a tabela por completo (e.g., o slider está ajustado até a data 13 de Setembro, mas a tabela mostra resultados apenas até o dia 4 de Setembro), pode ser um indicativo de que os arquivos de observação não se encontram no disco verificado. 
# 
# Para realizar o deploy do dashboard no GitHub, é necessário converter este notebook em um script executável, o que pode ser feito a partir da interface do Jupyter (`File` -> `Save and Export Notebook As...` -> `Executable Script`). A seguir, utilize o comando abaixo para converter o script em uma página HTML. Junto com a página, será gerado um arquivo JavaScript e ambos devem ser adicionados ao repositório, junto com o arquivo CSV.
#  
# ```
# panel convert SMNA-Dashboard.py --to pyodide-worker --out .
# ```
# 
# Para utilizar o dashboard localmente, utilize o comando a seguir:
# 
# ```
# panel serve SMNA-Dashboard.ipynb --autoreload --show
#  ```
#  
# ---
# Carlos Frederico Bastarz (carlos.bastarz@inpe.br), Setembro de 2023.

# In[1]:


import os
import glob
import pandas as pd
import hvplot.pandas
import holoviews as hv
import panel as pn
import datetime
import numpy as np

from datetime import timedelta

from math import pi

from bokeh import models
from bokeh.palettes import Category20c, Category20
from bokeh.plotting import figure
from bokeh.transform import cumsum

from bokeh.models.widgets.tables import DateFormatter

pn.extension(sizing_mode="stretch_width", notifications=True)
#pn.extension('perspective')
#pn.extension('tabulator')


# In[2]:


dfs = pd.read_csv('https://raw.githubusercontent.com/GAD-DIMNT-CPTEC/SMNA-Dashboard-ArmObs/main/mon_rec_obs_final.csv', header=[0], 
                  parse_dates=['Data do Download', 'Data da Observação'])

#dfs = pd.read_csv('mon_rec_obs_final.csv', header=[0], parse_dates=['Data do Download', 'Data da Observação'])

#dfs_edu = pd.read_csv('mon_rec_obs_final-edu.csv', header=[0], parse_dates=['Data do Download', 'Data da Observação', 'Início do Ciclo AD'])
#dfs_alex = pd.read_csv('mon_rec_obs_final-alex.csv', header=[0], parse_dates=['Data do Download', 'Data da Observação', 'Início do Ciclo AD'])


# In[ ]:


#dfs_edu


# In[ ]:


#dfs_alex


# In[ ]:


#dfs_edu['Data da Observação'] = pd.to_datetime(dfs_edu['Data da Observação'])
#dfs_alex['Data da Observação'] = pd.to_datetime(dfs_alex['Data da Observação'])


# In[ ]:


#dfs_edu['Diferença de Tempo'] = (dfs_edu['Data do Download'] - dfs_edu['Data da Observação']) - timedelta(hours=3)
#dfs_alex['Diferença de Tempo'] = (dfs_alex['Data do Download'] - dfs_alex['Data da Observação']) - timedelta(hours=3)


# In[ ]:


#dfs_edu['Diferença de Tempo'] = pd.to_timedelta(dfs_edu['Diferença de Tempo'])
#dfs_alex['Diferença de Tempo'] = pd.to_timedelta(dfs_alex['Diferença de Tempo'])


# In[3]:


dfs = dfs.drop(['Nome do Arquivo'], axis=1)


# In[4]:


dfs


# In[5]:


start_date = datetime.datetime(2023, 1, 1, 0)
end_date = datetime.datetime(2023, 10, 19, 0)

values = (start_date, end_date)

date_range_slider = pn.widgets.DatetimeRangePicker(name='Intervalo', value=values, enable_time=False)

units = ['KB', 'MB', 'GB', 'TB', 'PB']
otype = ['1bamua', '1bhrs4', 'airsev', 'atms', 'crisf4', 'eshrs3', 'esmhs', 'gome', 'gpsipw', 'gpsro', 'mtiasi', 'osbuv8', 'prepbufr', 'satwnd', 'sevcsr']
ftype = ['gdas', 'gfs']
synoptic_time_list = ['00Z', '06Z', '12Z', '18Z', '00Z e 12Z', '06Z e 18Z', '00Z, 06Z, 12Z e 18Z']

units_w = pn.widgets.Select(name='Unidade', options=units)
otype_w = pn.widgets.MultiChoice(name='Tipo de Observação', value=[otype[0]], options=otype, solid=False)
ftype_w = pn.widgets.MultiChoice(name='Tipo de Arquivo', value=[ftype[0]], options=ftype, solid=False)
synoptic_time = pn.widgets.RadioBoxGroup(name='Horário', options=synoptic_time_list, inline=False)

date_range = date_range_slider.value

######
dic_size = {}
def getSizeDic(dfsp, otype_w):
    dfsp_tot_down_otype = dfsp['Tamanho do Download (KB)'].loc[dfsp['Tipo de Observação'] == otype_w[-1]].sum(axis=0)
    dic_size[otype_w[-1]] = dfsp_tot_down_otype
    return dic_size       
   
def subDataframe(df, start_date, end_date):
    mask = (df['Data da Observação'] >= start_date) & (df['Data da Observação'] <= end_date)
    return df.loc[mask]

def subTimeDataFrame(synoptic_time):
    if synoptic_time == '00Z': time_fmt0 = '00:00:00'; time_fmt1 = '00:00:00'
    if synoptic_time == '06Z': time_fmt0 = '06:00:00'; time_fmt1 = '06:00:00'
    if synoptic_time == '12Z': time_fmt0 = '12:00:00'; time_fmt1 = '12:00:00'
    if synoptic_time == '18Z': time_fmt0 = '18:00:00'; time_fmt1 = '18:00:00'    
    
    if synoptic_time == '00Z e 12Z': time_fmt0 = '00:00:00'; time_fmt1 = '12:00:00'
    if synoptic_time == '06Z e 18Z': time_fmt0 = '06:00:00'; time_fmt1 = '18:00:00'
    
    if synoptic_time == '00Z e 06Z': time_fmt0 = '00:00:00'; time_fmt1 = '06:00:00'
    if synoptic_time == '12Z e 18Z': time_fmt0 = '12:00:00'; time_fmt1 = '18:00:00'    
    
    if synoptic_time == '00Z, 06Z, 12Z e 18Z': time_fmt0 = '00:00:00'; time_fmt1 = '18:00:00'   
    
    return time_fmt0, time_fmt1

def unitConvert(units_w):      
    if units_w == 'KB':
        factor = float(1)
        n1factor = 'Tamanho do Download (KB)'
        n2factor = 'Tamanho (KB)'
        n3factor = 'Total Armazenado (KB):'
    elif units_w == 'MB':
        factor = float(1 / (1024 ** 2))
        n1factor = 'Tamanho do Download (MB)'
        n2factor = 'Tamanho (MB)'
        n3factor = 'Total Armazenado (MB):'
    elif units_w == 'GB':
        factor = float(1 / (1024 ** 3))
        n1factor = 'Tamanho do Download (GB)'
        n2factor = 'Tamanho (GB)'
        n3factor = 'Total Armazenado (GB):'
    elif units_w == 'TB':
        factor = float(1 / (1024 ** 4))
        n1factor = 'Tamanho do Download (TB)'
        n2factor = 'Tamanho (TB)'
        n3factor = 'Total Armazenado (TB):'
    elif units_w == 'PB':
        factor = float(1 / (1024 ** 5))
        n1factor = 'Tamanho do Download (PB)'            
        n2factor = 'Tamanho (PB)'
        n3factor = 'Total Armazenado (PB):'
    
    return factor, n1factor, n2factor, n3factor

@pn.depends(otype_w, ftype_w, synoptic_time, date_range_slider.param.value)#, units_w)
def getTotDown(otype_w, ftype_w, synoptic_time, date_range):#, units_w):
    start_date, end_date = date_range
    dfs_tmp = dfs.copy()
    dfs2 = subDataframe(dfs_tmp, start_date, end_date)    
   
    #factor, n1factor, n2factor, n3factor = unitConvert(units_w)

    #dfs2[n1factor] = dfs2['Tamanho do Download (KB)'].multiply(factor)   
    
    time_fmt0, time_fmt1 = subTimeDataFrame(synoptic_time)
    
    if time_fmt0 == time_fmt1:
        dfsp = dfs2.loc[dfs2['Tipo de Observação'].isin(otype_w)].loc[dfs2['Tipo de Arquivo'].isin(ftype_w)].set_index('Data da Observação').at_time(str(time_fmt0)).reset_index()
    else:
        dfsp = dfs2.loc[dfs2['Tipo de Observação'].isin(otype_w)].loc[dfs2['Tipo de Arquivo'].isin(ftype_w)].set_index('Data da Observação').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')
            
        if synoptic_time == '00Z e 12Z':
            dfsp = dfsp.drop(dfsp.at_time('06:00:00').index).reset_index()
        elif synoptic_time == '06Z e 18Z':    
            dfsp = dfsp.drop(dfsp.at_time('12:00:00').index).reset_index()
        elif synoptic_time == '00Z, 06Z, 12Z e 18Z':
            dfsp = dfsp.reset_index()    
            
    #dfsp_tot_down = dfsp['Tamanho do Download (KB)'].sum(axis=0)
    
    factor = float(1 / (1024 ** 3))
    n1factor = 'Tamanho do Download (GB)'
    n2factor = 'Tamanho (GB)'
    n3factor = 'Total Armazenado (GB):'    
    
    #dfsp[n1factor] = dfsp['Tamanho do Download (KB)'].multiply(factor)
    dfsp[n1factor] = dfsp.loc[:, 'Tamanho do Download (KB)'].multiply(factor)
    
    dfsp_tot_down = dfsp[n1factor].sum(axis=0)
    
    #dfsp_tot_down = dfsp['Tamanho do Download (KB)'].multiply(factor).sum(axis=0)
    
    #tot_down = pn.indicators.Number(name=n3factor, value=dfsp_tot_down * factor, format='{value:.2f}', font_size='16pt', title_size='12pt')
    tot_down = pn.indicators.Number(name=n3factor, value=dfsp_tot_down, format='{value:.2f}', font_size='16pt', title_size='12pt')
    
    return pn.Column(tot_down, sizing_mode="stretch_both")

@pn.depends(otype_w, ftype_w, synoptic_time, date_range_slider.param.value, units_w)
def getTable(otype_w, ftype_w, synoptic_time, date_range, units_w):
    start_date, end_date = date_range

    dfs_tmp = dfs.copy()
    dfs2 = subDataframe(dfs_tmp, start_date, end_date)    
   
    factor, n1factor, n2factor, n3factor = unitConvert(units_w)

    #factor = float(1)
    #n1factor = 'Tamanho do Download (KB)'
    #n2factor = 'Tamanho (KB)'
    #n3factor = 'Total Armazenado (KB):'    
    
    #dfs2[n1factor] = dfs2['Tamanho do Download (KB)'].multiply(factor)   
    dfs2[n1factor] = dfs2.loc[:, 'Tamanho do Download (KB)'].multiply(factor)
    
    time_fmt0, time_fmt1 = subTimeDataFrame(synoptic_time)
    
    if time_fmt0 == time_fmt1:
        dfsp = dfs2.loc[dfs2['Tipo de Observação'].isin(otype_w)].loc[dfs2['Tipo de Arquivo'].isin(ftype_w)].set_index('Data da Observação').at_time(str(time_fmt0)).reset_index()
    else:
        dfsp = dfs2.loc[dfs2['Tipo de Observação'].isin(otype_w)].loc[dfs2['Tipo de Arquivo'].isin(ftype_w)].set_index('Data da Observação').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')
            
        if synoptic_time == '00Z e 12Z':
            dfsp = dfsp.drop(dfsp.at_time('06:00:00').index).reset_index()
        elif synoptic_time == '06Z e 18Z':    
            dfsp = dfsp.drop(dfsp.at_time('12:00:00').index).reset_index()
        elif synoptic_time == '00Z, 06Z, 12Z e 18Z':
            dfsp = dfsp.reset_index()      
    
    bokeh_formatters = {
        'Diferença de Tempo': models.DateFormatter(format='%d days %H:%M:%S'),
    }

    # Simples
    df_tb = pn.pane.DataFrame(dfsp, 
                              name='DataFrame', 
                              height=600, 
                              #bold_rows=True,
                              #border=15,
                              decimal=',',
                              #formatters=bokeh_formatters,
                              #col_space=10,
                              #index_names=False,
                              index=True,
                              show_dimensions=True,
                              #justify='center',
                              #sparsify=True,
                              sizing_mode='stretch_both',
                             )
    
    # Avançado
#    df_tb = pn.widgets.DataFrame(dfsp, 
#                                 name='DataFrame', 
#                                 height=600, 
#                                 show_index=True, 
#                                 frozen_rows=0, 
#                                 frozen_columns=2, 
#                                 autosize_mode='force_fit', 
#                                 fit_columns=True,
#                                 formatters=bokeh_formatters,
#                                 auto_edit=False,
#                                 reorderable=True,
#                                 sortable=True,
#                                 text_align='center',
#                                )

    # Mais Avançado (e pesado)
#    df_tb = pn.widgets.Tabulator(dfsp, 
#                                 name='DataFrame', 
#                                 frozen_rows=[0,1],
#                                 frozen_columns=[2], 
#                                 pagination=None,
#                                 selectable='toggle',
#                                 show_index=True,
#                                 theme='default',
#                                 formatters=bokeh_formatters,
#                                )

#    df_tb = pn.pane.Perspective(dfsp,
#                               name='DataFrame',
#                               selectable=True,
#                               theme='material',
#                               toggle_config=False,
#                               height=600,
#                               plugin_config={
#                                   'Diferença de Tempo': {"timeStyle": "Simple"},
#                               }
#                               )
    
    return pn.Column(df_tb, sizing_mode="stretch_both")
       
@pn.depends(otype_w, ftype_w, synoptic_time, date_range_slider.param.value)#, units_w)
def plotLine(otype_w, ftype_w, synoptic_time, date_range):#, units_w):
    for count, i in enumerate(otype_w):
        for count2, j in enumerate(ftype_w):
            if count == 0:
                start_date, end_date = date_range
                dfs_tmp = dfs.copy()
                dfs2 = subDataframe(dfs_tmp, start_date, end_date)
            
                time_fmt0, time_fmt1 = subTimeDataFrame(synoptic_time)
            
                notype = otype_w[count]
            
                if time_fmt0 == time_fmt1:
                    dfsp = dfs2.loc[dfs2['Tipo de Observação'] == str(i)].loc[dfs2['Tipo de Arquivo'] == str(j)].set_index('Data da Observação').at_time(str(time_fmt0)).reset_index()
                else:
                    dfsp = dfs2.loc[dfs2['Tipo de Observação'] == str(i)].loc[dfs2['Tipo de Arquivo'] == str(j)].set_index('Data da Observação').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')                
            
                    if synoptic_time == '00Z e 12Z':
                        dfsp = dfsp.drop(dfsp.at_time('06:00:00').index).reset_index()
                    elif synoptic_time == '06Z e 18Z':    
                        dfsp = dfsp.drop(dfsp.at_time('12:00:00').index).reset_index()
                    elif synoptic_time == '00Z, 06Z, 12Z e 18Z':
                        dfsp = dfsp.reset_index()              
            
                #factor, n1factor, n2factor, n3factor = unitConvert(units_w)
            
                factor = float(1 / (1024 ** 2))
                n1factor = 'Tamanho do Download (MB)'
                n2factor = 'Tamanho (MB)'
                n3factor = 'Total Armazenado (MB):'                
            
                #dfsp[n1factor] = dfsp['Tamanho do Download (KB)'].multiply(factor)   
                dfsp[n1factor] = dfsp.loc[:, 'Tamanho do Download (KB)'].multiply(factor)
            
                df_pl = dfsp.hvplot.line(x='Data da Observação', xlabel='Data', y=n1factor, 
                                     ylabel=str(n2factor), label=str(notype), rot=90, grid=True, 
                                     line_width=2, responsive=True,
                                     color=Category20[20][count], min_height=550, min_width=850)
            
                sdf_pl = dfsp.hvplot.scatter(x='Data da Observação', y=n1factor, label=str(notype), responsive=True, color=Category20[20][count],
                                             min_height=550, min_width=850)
            
            else:
                
                start_date, end_date = date_range
                dfs_tmp = dfs.copy()
                dfs2 = subDataframe(dfs_tmp, start_date, end_date)            
            
                time_fmt0, time_fmt1 = subTimeDataFrame(synoptic_time)
            
                notype = otype_w[count]
            
                if time_fmt0 == time_fmt1:
                    dfsp = dfs2.loc[dfs2['Tipo de Observação'] == str(i)].loc[dfs2['Tipo de Arquivo'] == str(j)].set_index('Data da Observação').at_time(str(time_fmt0)).reset_index()
                else:
                    dfsp = dfs2.loc[dfs2['Tipo de Observação'] == str(i)].loc[dfs2['Tipo de Arquivo'] == str(j)].set_index('Data da Observação').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')                
            
                    if synoptic_time == '00Z e 12Z':
                        dfsp = dfsp.drop(dfsp.at_time('06:00:00').index).reset_index()
                    elif synoptic_time == '06Z e 18Z':    
                        dfsp = dfsp.drop(dfsp.at_time('12:00:00').index).reset_index()
                    elif synoptic_time == '00Z, 06Z, 12Z e 18Z':
                        dfsp = dfsp.reset_index()              
                
                #factor, n1factor, n2factor, n3factor = unitConvert(units_w)
                
                factor = float(1 / (1024 ** 2))
                n1factor = 'Tamanho do Download (MB)'
                n2factor = 'Tamanho (MB)'
                n3factor = 'Total Armazenado (MB):'   
                
                #dfsp[n1factor] = dfsp['Tamanho do Download (KB)'].multiply(factor) 
                dfsp[n1factor] = dfsp.loc[:, 'Tamanho do Download (KB)'].multiply(factor)
                    
                df_pl *= dfsp.hvplot.line(x='Data da Observação', xlabel='Data', y=n1factor, 
                                      ylabel=n2factor, label=str(notype), rot=90, grid=True, 
                                      line_width=2, responsive=True,
                                      color=Category20[20][count], min_height=550, min_width=850)
    
                sdf_pl *= dfsp.hvplot.scatter(x='Data da Observação', y=n1factor, label=str(notype), responsive=True, color=Category20[20][count], 
                                              min_height=550, min_width=850)
    
    return pn.Column(df_pl*sdf_pl, sizing_mode='stretch_width')
    
@pn.depends(otype_w, ftype_w, synoptic_time, date_range_slider.param.value)
def plotSelSize(otype_w, ftype_w, synoptic_time, date_range):
    start_date, end_date = date_range
    #dfs_tmp = dfs.copy()
    #dfs2 = subDataframe(dfs_tmp, start_date, end_date) 
    dfs2 = subDataframe(dfs, start_date, end_date) 
    
    time_fmt0, time_fmt1 = subTimeDataFrame(synoptic_time)    
        
    if time_fmt0 == time_fmt1:
        dfsp = dfs2.loc[dfs2['Tipo de Observação'].isin(otype_w)].loc[dfs2['Tipo de Arquivo'].isin(ftype_w)].set_index('Data da Observação').at_time(str(time_fmt0)).reset_index()
    else:
        dfsp = dfs2.loc[dfs2['Tipo de Observação'].isin(otype_w)].loc[dfs2['Tipo de Arquivo'].isin(ftype_w)].set_index('Data da Observação').between_time(str(time_fmt0), str(time_fmt1), inclusive='both')
            
        if synoptic_time == '00Z e 12Z':
            dfsp = dfsp.drop(dfsp.at_time('06:00:00').index).reset_index()
        elif synoptic_time == '06Z e 18Z':    
            dfsp = dfsp.drop(dfsp.at_time('12:00:00').index).reset_index()
        elif synoptic_time == '00Z, 06Z, 12Z e 18Z':
            dfsp = dfsp.reset_index()      
    
    factor = float(1)
    n1factor = 'Tamanho do Download (KB)'
    n2factor = 'Tamanho (KB)'
    n3factor = 'Total Armazenado (KB):'    
    
    # Tamanho do download (ou do espaço ocupado), de acordo com a seleção da tabela
    dfsp_tot_down = dfsp['Tamanho do Download (KB)'].sum(axis=0)
    
    dfsp_dic_down = getSizeDic(dfsp, otype_w)
    
    # Remove a observação da lista a ser plotada         
    for key in list(dfsp_dic_down):
        if key not in otype_w:
            del dfsp_dic_down[key]        
        
    data = pd.Series(dfsp_dic_down).reset_index(name='Tamanho do Download (KB)').rename(columns={'index':'Tipo de Observação'})  
    
    # Acrescenta uma nova coluna 'Tamanho Relativo' à série data
    data['Tamanho Relativo (%)'] = (data['Tamanho do Download (KB)'] / dfsp_tot_down) * 100

    data['angle'] = (data['Tamanho do Download (KB)'] / data['Tamanho do Download (KB)'].sum()) * (2 * pi)
    if len(dfsp_dic_down) == 0:
        data['color'] = ''
    elif len(dfsp_dic_down) == 1:
        data['color'] = Category20[3][0]
    elif len(dfsp_dic_down) == 2:
        data['color'] = Category20[3][:2]
    elif len(dfsp_dic_down) > 2:   
        data['color'] = Category20[len(dfsp_dic_down)]

    p = figure(min_width=500, min_height=550, title='Tamanho Relativo (%)', #toolbar_location=None, tools="hover", 
               tooltips="@{Tipo de Observação}: @{Tamanho Relativo (%)}", x_range=(-0.6, 1.15))    
    
    r = p.wedge(x=0, y=1, radius=0.55,
                start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
                line_color='white', fill_color='color', legend_field='Tipo de Observação', 
                source=data)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color=None

    #return pn.Column(pn.pane.Bokeh(p), sizing_mode='stretch_width')    
    return pn.pane.Bokeh(p)
    
######    

notes = """
### Notas:

* **Data da observação**: refere-se à data do ciclo de análise (e.g., 2023-01-07 00:00:00 representa a análise das 2023010700);
* **Tamanho do Download**: refere-se ao tamanho em KB (kilobytes) do arquivo de observação armazenado em disco na máquina XC50;
* **Data do Download**: refere-se à data em que o arquivo de observação foi criado em disco na máquina XC50;
* **Fuso Horário**: refere-se ao fuso horário de Brasília em relação ao GMT (GMT-3);
* **Início do Ciclo AD**: refere-se ao horário de início do ciclo de assimilação de dados registrado nas primeiras linhas do arquivo de log do GSI (este arquivo de log é sempre o último gerado, caso outras tentativas de se realizar o sistema tenham sido feitas);
* **Tipo de Arquivo**: refere-se aos arquivos do tipo `gdas` ou `gfs`. Ambos são disseminados pelo NCEP, mas os arquivos `gdas` possuem mais informações do que os arquivos `gfs`. Os arquivos `gfs` são disseminados antes do que os arquivos `gdas`;
* **Horário Sinótico**: refere-se ao horário sinótico do ciclo de análise ao qual as observações pertencem;
* **Tipo de Observação**: refere-se ao mnemônico utilizado pelo GSI para identificar os diferentes tipo de observações;
* **Diferença de Tempo**: refere-se à diferença entre a data da observação e a data do donwload. Efetivamente, é calculado como: `dfs['Diferença de Tempo'] = (dfs['Data do Download'] - dfs['Data da Observação']) - timedelta(hours=3)`, sendo o `timedelta(hours=3)` subtraído da diferença entre as datas para descontar a diferença do fuso horário.

Além disso, no gráfico de linhas os tamanhos dos arquivos são mostrados em MB (megabytes) e o total armazenado, em GB (gigabytes). Para as conversões entre as unidades (KB para MB e GB), considera-se que 1 MB(GB) = 1024 KB(MB).
"""

card_parameters = pn.Card(date_range_slider, synoptic_time, ftype_w, otype_w, title='Parâmetros', collapsed=False)

tabs_contents = pn.Tabs(
    ('Gráficos', pn.Row(plotLine, plotSelSize)),
    ('Tabela', getTable), 
    dynamic=False)

pn.template.FastListTemplate(
    site="SMNA Dashboard", title="Armazenamento Observações (ArmObs)",
    sidebar = [card_parameters],
    main=["Visualização do armazenamento das observações do **SMNA**", tabs_contents, getTotDown, notes]
#).show();
).servable();


# In[ ]:





# In[ ]:




