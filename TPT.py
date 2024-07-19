import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import streamlit as st 
import seaborn as sns
from matplotlib.ticker import MaxNLocator
import plotly.graph_objects as go

st.set_page_config(page_title="TPT", page_icon="rocket", layout="wide")

#Def for Age Group Columns
    

def categorize_age_group_detail(age):
    if age >= 0 and age < 5:
        return '0-4 yrs'
    elif age >=5 and age < 10:
        return '5-9 yrs'
    elif age >= 10 and age < 15:
        return '10-14 yrs'
    elif age >= 15 and age < 25:
        return '15-24 yrs'
    elif age >= 25 and age < 35:
        return '25-34 yrs'
    elif age >= 35 and age < 45:
        return '35-44 yrs'
    elif age >= 45 and age < 55:
        return '45-54 yrs'
    elif age >= 55 and age < 65:
        return '55-64 yrs'
    else:
        return '> 65 yrs'

@st.cache_data # Cache the data to improve performance
def load_data():
   # Load the data
    df = pd.read_excel("TPT data START FROM 2022_new.xlsx","TPT Registrar Entry Form")
    # Drop rows
    df.dropna(subset=['Year'], inplace=True)
    # Convert Year to Int
    df['Year'] = df['Year'].astype(int)
    
    #rename columns
    df.columns = df.columns.str.split('\n').str[0].str.lower().str.replace(' ', '_')
    df.rename(columns={'state/region_name':'SR','township_name':'tsp','reporting_period':'qtr',
                    'tpt_register_no.':'TPT_no',"township_tb_reg_number_of_index_tbcases": "index_TB_no",
                   "type_of_index":"index_type", "tpt_registration_date_(mm/dd/yy)" : "TPT_reg_date", 
                   "hiv_status_(pos/neg/unk)" : "hiv", "tpt_discontinuation_date_(mm/dd/yy)":"tpt_stop_date",
                   "treatment_outcome" : "outcome" },inplace=True)
    
    #drop unnecessary columns
    df.drop(['month',  'index_TB_no','index_type','gp_name','TPT_reg_date',
         'tpt_stop_date', 'remark'], axis=1, inplace=True)
    
    # Data transformations
    df['sex'].replace('f','F', inplace = True)
    df['sex'].replace('m','M', inplace = True)
    df['hiv'].replace('p','P', inplace = True)
    df['hiv'].replace('n','N', inplace = True)

    df['sex'].replace('F','Female', inplace = True)
    df['sex'].replace('M','Male', inplace = True)
    df['sex'].replace('F','Female', inplace = True)
    df['sex'].replace('M','Male', inplace = True)

    df['hiv'].replace('P','Pos', inplace = True)
    df['hiv'].replace('N','Neg', inplace = True)
    df['hiv'].replace('U','Unk', inplace = True)

    df['outcome'].replace('C','Complete', inplace = True)
    df['outcome'].replace('I','Incomplete', inplace = True)
    df['outcome'].replace('TB','Develop TB', inplace = True)
    df['outcome'].replace('DC','Discontinue by patient', inplace = True)
    df['outcome'].replace('SE','Discontinue due to Side Effect', inplace = True)
    df['outcome'].replace('N','Not evaluated', inplace = True)
    df['outcome'].replace('D','Died', inplace = True)

    
    df['age_group_detail'] = df['age'].apply(categorize_age_group_detail)

    #O8 Dataframe
    df_o8 = df.copy()
    df_o8['Reported_yr'] = df_o8['year'] + 1
    return df, df_o8

df, df_o8 = load_data()

   

# ---- SIDEBAR ----
def handle_all_selection(selection, options):
    if 'All' in selection:
        return options  # Returns all options if 'All' is selected
    return selection  # Otherwise, return the selection


st.sidebar.header("Please Filter Here:")

df_sr_sort= df.sort_values('SR', ascending= True)

State_options = list(df_sr_sort["SR"].unique())
State = st.sidebar.multiselect(
    "Select the State & Region:",
   options=['All'] + State_options,
    default= ['Yangon'])

State = handle_all_selection(State, State_options)

df_tsp_sort = df.query( "SR == @State").sort_values('tsp', ascending= True)


Township_options = list(df_tsp_sort["tsp"].unique())
Township = st.sidebar.multiselect(
    "Select the Township:",
    options= ['All'] + Township_options,
    default= ['All'])

Township = handle_all_selection(Township, Township_options)


Year = st.sidebar.multiselect(
    "Select the Year:",
   options=df["year"].unique(),
    default= df["year"].unique())

selected_age = st.sidebar.slider(
    "Select the Age Range:",
    min_value=int(df["age"].min()),
    max_value=int(df["age"].max()),
    value=(int(df["age"].min()), int(df["age"].max())))

selected_sex = st.sidebar.multiselect(
    "Select the Gender:",
    options=df["sex"].unique(),
    default=['Male','Female'])

TPT_Regimen_Type = st.sidebar.multiselect(
    "Select the TPT Regimen Type:",
   options=df["tpt_regimens"].unique(),
    default= df["tpt_regimens"].unique())

# Apply filter
df = df.query( 
    "SR == @State & tsp == @Township & year == @Year & age >= @selected_age[0] & age <= @selected_age[1] & sex in @selected_sex & tpt_regimens==@TPT_Regimen_Type"
)

# Apply filter for O8
df_o8 = df_o8.query( 
    "SR == @State & tsp == @Township & Reported_yr == @Year & age >= @selected_age[0] & age <= @selected_age[1] & sex in @selected_sex & tpt_regimens==@TPT_Regimen_Type"
)

# ---- MAINPAGE ----
st.title(":rocket: TB Preventive Therapy")
st.markdown("##")

# Display DataFrame or a message if empty
if df.empty:
    st.write('DataFrame is empty!')
    
else:
    total_cases = df["year"].count()
    st.subheader ('Total TPT cases: ')
    st.subheader (f"{total_cases}")

    #year dataframe
    df_year= df.groupby(['year'], as_index=False).agg({'tsp':'count'})
    df_year.rename(columns={'tsp':'patients'}, inplace=True)

    #year chart
    fig_yr = px.line(df_year,x='year',y='patients',title='Yearly TPT Cases')
    fig_yr.update_xaxes(tick0= 0,dtick = 1 )
    
    st.plotly_chart(fig_yr, use_container_width= True)

    #qtr df
    df_qtr= df.groupby(['qtr'], as_index=False).agg({'year':'count'})
    df_qtr.rename(columns={'year':'patients'}, inplace=True)

    #qtr chart
    fig_qtr= px.line(df_qtr,x='qtr',y='patients',title='Quarterly TPT Cases')
    st.plotly_chart(fig_qtr, use_container_width= True)


    #SR dataframe
    df_sr= df.groupby(['SR'],as_index=False).agg({'year':'count'})
    df_sr = df_sr.sort_values('year', ascending= False)

    # States and Regions Bar Plot
    
    fig_SR= px.bar(df_sr,x = 'SR', y= 'year', labels={'year':'Patients'},
                        title='Total TPT cases of States and Regions', color='SR', 
                             color_discrete_sequence=px.colors.diverging.balance)
    fig_SR.update_layout(showlegend=False)

    st.plotly_chart(fig_SR, use_container_width= True)

    #tsp dataframe
    df_tsp= df.groupby(['tsp'],as_index=False).agg({'year':'count'}).sort_values('year', ascending= False)
    df_tsp.insert(0, 'Serial No', range(1, 1 + len(df_tsp)))
    df_tsp.rename(columns={'year':'Total Cases'},inplace=True)
    
    st.subheader('Township with Highest TPT Cases')
    st.dataframe(df_tsp, hide_index=True, use_container_width= True)
   

    #Tsps Bar Plot
    fig_tsp= px.bar(df_tsp, x = 'tsp', y= 'Total Cases',
                        title='Township-wise TPT Holdings', color='tsp', 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_tsp.update_layout(showlegend=False)
   

    st.plotly_chart(fig_tsp, use_container_width= True)

    #sex data frame
    df_sex=df.groupby(['SR','sex']).size().reset_index(name='Patient_count')

    #sex chart
    color_map = {'Female':'blue','Male':'orange'}
    fig_sex= px.bar(df_sex,x='SR',y='Patient_count',color= 'sex',
           barmode ='group',
           title='Gender in TPT',
           color_discrete_map=color_map)
    fig_sex.update_layout(showlegend=False)
    #st.plotly_chart(fig_sex, use_container_width= True)

    #Sex Based Data Frame
    df_sex_all= df.groupby(['sex'], as_index= False).agg({'year':'count'})

    #Sex Based Pie Plot
    colors= {'Male':'blue','Female':'orange'}
    fig_sex_all = px.pie(df_sex_all, names= 'sex',values='year',labels={'year':'Patients'},
                            title='Gender Contribution',
                    color= 'sex',color_discrete_map= colors)
    
    st.plotly_chart(fig_sex_all, use_container_width= True)

    #Age group dfs
   
    df_age_group= df.groupby(['age_group'], as_index= False).agg({'year':'count'})


    df_age_group_detail= df.groupby(['age_group_detail'], as_index= False).agg({'year':'count'})


    #Age group charts
    

    fig_age_group = px.histogram(df_age_group, x= 'age_group',y='year',labels={'year':'Patients'},
                        title='Age category of TPT cases', color='age_group', 
                             color_discrete_sequence=px.colors.sequential.Viridis,barmode='overlay',
                             category_orders=dict(age_group=['0-4 yrs','5-14 yrs','15-60 yrs','> 60 yrs']))
    fig_age_group.update_layout(showlegend=False)

    st.plotly_chart(fig_age_group, use_container_width= True)


    fig_age_group_detail = px.histogram(df_age_group_detail, x= 'age_group_detail',y='year',labels={'year':'Patients'},
                        title='Age category detail of TPT cases', color='age_group_detail', 
                             color_discrete_sequence=px.colors.sequential.Aggrnyl,barmode='overlay',
                             category_orders=dict(age_group_detail=['0-4 yrs','5-9 yrs','10-14 yrs','15-24 yrs','25-34 yrs',
                                                             '35-44 yrs','45-54 yrs','55-64 yrs','> 65 yrs']))
    fig_age_group_detail.update_layout(showlegend=False)

    st.plotly_chart(fig_age_group_detail, use_container_width= True)

    #TPT Regimen df
    df_tpt_reg =df.groupby(['tpt_regimens'], as_index= False).agg({'year':'count'})

    #TPT Regimen chart
    colors= {'3HP':'teal','6H':'orange'}
    fig_tpt_reg = px.pie(df_tpt_reg, names= 'tpt_regimens',values='year',labels={'year':'Patients','tpt_regimens':'TPT Regimens'},
                        title='TPT Regimen',
                  color= 'tpt_regimens',color_discrete_map= colors, hole= 0.2)
    fig_tpt_reg.update_traces(pull=[0.4, 0.2, 0, 0])
    st.plotly_chart(fig_tpt_reg, use_container_width= True)


   
    #HIV df
    df_hiv= df.groupby(['hiv'],as_index=False).agg({'year':'count'})

    
    #HIV status known df
    df_hiv_known= df.groupby(['hiv'],as_index=False).agg({'year':'count'})
    df_hiv_known['hiv'].replace({'Neg':'Known','Pos':'Known'}, inplace=True)
    df_hiv_known= df_hiv_known.groupby(['hiv'],as_index=True).agg({'year': 'sum'})
    if 'Known' in df_hiv_known.index and 'Unk' in df_hiv_known.index:
        pass
    elif 'Unk' in df_hiv_known.index:
        df_hiv_known.loc['Known']= 0
    else:
        df_hiv_known.loc['Unk']= 0

    count_hiv_known= df_hiv_known.loc['Known']
    count_hiv_unknown= df_hiv_known.loc['Unk']
    percent_hiv_known= count_hiv_known['year']/(count_hiv_known['year'] + count_hiv_unknown['year'])*100

    #HIV status known chart
    fig_hiv_known_percent = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = percent_hiv_known,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "HCT Testing Percent"},
    gauge= {'axis': {'range': [0,100]}}))

    st.plotly_chart(fig_hiv_known_percent, use_container_width= True)

    
    #HIV chart
    colors= {'Neg':'blue','Unk':'grey','Pos':'red'}
    fig_hiv = px.pie(df_hiv, names= 'hiv',values='year',labels={'year':'Patients'},title='HCT result',
                  color= 'hiv',color_discrete_map= colors)
    st.plotly_chart(fig_hiv, use_container_width= True)


    #Tx outcome dfs
    df_outcome= df_o8.groupby(['outcome'], as_index =False).agg({'year':'count'})
       

    
    #TSR df
    df_tsr= df_o8.groupby(['outcome'], as_index =False).agg({'year':'count'})

    df_tsr['outcome'].replace({'Complete':'Tx success','Incomplete':'Tx not success', 'Develop TB':'Tx not success', 
                           'Discontinue by patient':'Tx not success','Discontinue due to Side Effect':'Tx not success',
                                     'Not evaluated':'Tx not success', 'Died': 'Tx not success'},
                          inplace=True)
    df_tsr = df_tsr.groupby(['outcome'], as_index =True).agg({'year':'sum'})

    if 'Tx success' in df_tsr.index and 'Tx not success' in df_tsr.index:
        pass
    elif 'Tx success' in df_tsr.index:
        df_tsr.loc['Tx not success']= 0
    else:
        df_tsr.loc['Tx success']= 0

    count_tsr_success = df_tsr.loc['Tx success']
    count_tsr_not_success = df_tsr.loc['Tx not success']
    count_tsr_denominator = count_tsr_not_success['year'] + count_tsr_success['year']

    percent_tsr = (count_tsr_success['year']/count_tsr_denominator)*100

    #TSR chart
    fig_tsr_percent = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = percent_tsr,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': "TSR Percent"},
    gauge= {'axis': {'range': [0,100]},
            'threshold':{'line':{'color':"red", 'width': 4}, 'thickness': 0.75, 'value':90}}))

    st.plotly_chart(fig_tsr_percent, use_container_width= True)

    

    #Tx outcome chart
    colors= {'Complete':'blue','Died':'black','Incomplete':'grey','Develop TB':'orange','Discontinue by patient':'purple',
         'Not Evaluated':'red','Discontinue due to Side Effect':'yellow'}
    fig_outcome = px.pie(df_outcome, names= 'outcome',values='year',labels={'year':'Patients'},
                        title='Outcome of TPT cases from previous year',
                  color= 'outcome',color_discrete_map= colors, hole= 0.4)
    fig_outcome.update_traces(pull=[0,0.2, 0.4, 0.2, 0.4,0.6, 0])
    st.plotly_chart(fig_outcome, use_container_width= True)

    



