import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
import plotly.express as px
from PIL import Image


def process_main_page():
    show_main_page()
    process_side_bar_inputs()


def show_main_page():
    image = Image.open('data/wage.jpg')
    # image = image.resize((round(image.size[0]), round(image.size[1] * 0.7)))

    st.set_page_config(
        layout="wide",
        initial_sidebar_state="auto",
        page_title="Анализ зарплат в России",
        page_icon=image,
    )
    st.write(
        """
        # Анализ зарплат в России
        """
    )
    st.image(image)


def read_df(path="data/.csv"):
    df = pd.read_csv(path, delimiter=';')
    return df


def show_conclusions(industry, enabled=True):
    mapping = {
        'инфляция': 'По графику четко видны годы максимального и минимального уровня инфляции.',
        'образование': 'Судя по графикам средней зарплаты с учетом инфляции и без и графику динамики изменения зп с учетом инфляции и без, можно сделать вывод, что средняя зп в отрасли образования растет из года в год, при этом характерно влияние кризисов на уровень зп.',
        'строительство': 'Судя по графикам средней зарплаты с учетом инфляции и без и графику динамики изменения зп с учетом инфляции и без, можно сделать вывод, что наибольший рост реальной зп был в период 2001 года. Стоит заметить, что в период 2009 года, несмотря на падение уровня номинальной зп, реальная зп (без учета инфляции) выросла. Это можно объяснить заметным снижением уровня инфляции с пикого 2008 года - 13.28% до 8.80% в 2009.',
        'здравоохранение': 'Судя по графикам средней зарплаты с учетом инфляции и без и графику динамики изменения зп с учетом инфляции и без, можно сделать вывод, что наибольший рост реальной зп был в период 2002 года, наименьший - в 2021. Стоит обратить внимание, что несмотря на повышение номинальной средней зп в 2021 году на 2% по сравнению с 2020 годом, уровень реальной зп (без учета инфляции) снизился на 1%',
        'авто': 'Коэффициент корреляции =~ -0.75.  \nСуществует сильная обратная линейная корреляционная зависимость между числом продаваемых авто и уровнем реальной зп',
        'безработица': 'Коэффициент корреляции =~ -0.88.  \nСуществует сильная обратная линейная корреляционная зависимость между процентом безработных и уровнем реальной зп'
    }
    if enabled:
        st.write('### Выводы:')
        st.write(mapping[industry])


def plot(graphs, title):
    fig = plt.figure(figsize=(14, 4))
    for graph in graphs:
        plt.plot(graph['x'], graph['y'], marker='o', color=graph['color'], label=graph['label'])
        plt.xlabel(graph['xlabel'])
        plt.ylabel(graph['ylabel'])
    plt.xticks(graphs[0]['x'])
    plt.title(title)
    plt.legend()
    plt.grid()
    st.pyplot(plt.gcf())


def bar(bars, title, width=0.25, figsize=(14, 4)):
    plt.figure(figsize=figsize)
    for i, bar in enumerate(bars):
        plt.bar(bar['x'] + width * i, bar['y'], color=bar['color'], width=width, edgecolor='black',label=bar['label'])
    plt.ylim([0.9, 1.7])
    plt.xticks(bars[0]['x'])
    plt.xlabel(bar['xlabel'])
    plt.ylabel(bar['ylabel'])
    plt.title(title) 
    plt.legend()
    plt.grid()
    st.pyplot(plt.gcf())


def analyse_industry(industry_name, df_industry_with_inflation, show_dynamics=True):
    st.write(f'## Отрасль "{industry_name}"')
    st.write(f'### Данные по отрасли "{industry_name}":', df_industry_with_inflation.head())
    plot(
        title=f'Отрасль "{industry_name}" - графики средней зп с учетом инфляции и без',
        graphs=[
            {
                'x': df_industry_with_inflation['Год'],
                'xlabel': 'год',
                'y': df_industry_with_inflation['Средняя зарплата'],
                'ylabel': 'тыс. рублей',
                'color': 'green',
                'label': 'с учетом инфляции (номинальная)'
            },
            {
                'x': df_industry_with_inflation['Год'],
                'xlabel': 'год',
                'y': df_industry_with_inflation['Реальная зарплата'],
                'ylabel': 'тыс. рублей',
                'color': 'blue',
                'label': 'без учета инфляции (реальная)'
            },
            ]
        )
    if show_dynamics:
        bar(
            title=f'Отрасль "{industry_name}" - динамика изменения зп с учетом инфляции и без',
            bars=[
                {
                    'x': df_industry_with_inflation['Год'][1:],
                    'xlabel': 'год',
                    'y': df_industry_with_inflation['Изменение зп'][1:],
                    'ylabel': 'коэфф',
                    'color': 'blue',
                    'label': 'изменение зп с учетом инфляции'
                },
                {
                    'x': df_industry_with_inflation['Год'][1:],
                    'xlabel': 'год',
                    'y': df_industry_with_inflation['Реальное изменение зп'][1:],
                    'ylabel': 'коэфф',
                    'color': 'green',
                    'label': 'изменение зп без учета инфляции (реальное)'
                }
                ]
            )


def correlation(df, x, y):
    fig = px.scatter(df, x=x, y=y)
    st.plotly_chart(fig)
    st.write(f'#### Коэффициент корреляции = {df[x].corr(df[y])}')


def create_industry_df_with_inflation(df_industry, df_inflation):
    df_industry_with_inflation = pd.merge(df_industry, df_inflation, on='Год', how='outer')
    df_industry_with_inflation['Реальная зарплата'] = df_industry_with_inflation['Средняя зарплата'] / (1 + 0.01 * df_industry_with_inflation['Инфляция'])
    df_industry_with_inflation['Изменение зп'] = df_industry_with_inflation['Средняя зарплата'] / df_industry_with_inflation['Средняя зарплата'].shift()
    df_industry_with_inflation['Реальное изменение зп'] = df_industry_with_inflation['Реальная зарплата'] / df_industry_with_inflation['Реальная зарплата'].shift()
    return df_industry_with_inflation


def process_side_bar_inputs():
    user_input_data = sidebar_input_features()

    inflation_enabled = user_input_data['inflation_enabled']
    conclusions_enabled = user_input_data['conclusions_enabled']
    industries = user_input_data['industries']
    extra_research_auto_enabled = user_input_data['extra_research_auto_enabled']
    extra_research_unemployment_enabled = user_input_data['extra_research_unemployment_enabled']

    # plot inflation
    df_inflation = read_df(path="data/инфляция.csv")
    if inflation_enabled:
        st.write('## Уровень инфляции')
        plot(
            title='Уровень инфляции',
            graphs=[{
                    'x': df_inflation['Год'],
                    'xlabel': 'год',
                    'y': df_inflation['Инфляция'],
                    'ylabel': 'процент',
                    'color': 'green',
                    'label': 'Уровень инфляции'
                }]
            )
        show_conclusions('инфляция', enabled=conclusions_enabled)

    # analyse industries
    for industry_name in industries:
        df_industry = read_df(path=f'data/{industry_name}.csv')
        df_industry_with_inflation = create_industry_df_with_inflation(df_industry, df_inflation)
        analyse_industry(industry_name, df_industry_with_inflation)
        show_conclusions(industry_name, enabled=conclusions_enabled)

    # extra research
    if extra_research_auto_enabled:
        st.write('## Дополонительное исследование - корреляция продаж авто и реальной средней зп')
        df_auto = read_df('data/продажи-авто.csv')
        plot(
            title='Продажи авто',
            graphs=[{
                    'x': df_auto['Год'],
                    'xlabel': 'год',
                    'y': df_auto['Число проданных новых авто'],
                    'ylabel': 'число проданных авто',
                    'color': 'green',
                    'label': 'Число проданных авто'
                }]
            )

        # all industries
        df_all_industries = read_df('data/средняя-зп-по-всем-отраслям.csv')
        df_all_industries_with_inflation = create_industry_df_with_inflation(df_all_industries.loc[df_all_industries['Год'] >= 2007], df_inflation.loc[df_inflation['Год'] >= 2007])
        analyse_industry('Все', df_all_industries_with_inflation, show_dynamics=False)


        # correlation 
        correlation_df = pd.concat([df_all_industries_with_inflation.loc[df_all_industries_with_inflation['Год'] >= 2007]['Реальная зарплата'],
                    df_auto['Число проданных новых авто']], axis=1)

        correlation(correlation_df,'Реальная зарплата', 'Число проданных новых авто')
        show_conclusions('авто', enabled=conclusions_enabled)

    if extra_research_unemployment_enabled:
        st.write('## Дополонительное исследование - корреляция уровня безработицы и реальной средней зп')
        df_unemployment = read_df('data/уровень-безработицы.csv')
        plot(
            title='Уровень безработицы',
            graphs=[{
                    'x': df_unemployment['Год'],
                    'xlabel': 'год',
                    'y': df_unemployment['Процент безработных'],
                    'ylabel': 'процент',
                    'color': 'green',
                    'label': 'уровень безработицы'
                }]
            )

        # all industries
        df_all_industries = pd.read_csv("data/средняя-зп-по-всем-отраслям.csv", delimiter=';')
        df_all_industries_with_inflation = create_industry_df_with_inflation(df_all_industries, df_inflation)
        analyse_industry('Все', df_all_industries_with_inflation, show_dynamics=False)

        # correlation
        correlation_df = pd.concat([df_all_industries_with_inflation['Реальная зарплата'], df_unemployment['Процент безработных']], axis=1)
        correlation(correlation_df, 'Реальная зарплата', 'Процент безработных')
        show_conclusions('безработица', enabled=conclusions_enabled)

def sidebar_input_features():
    conclusions_enabled=st.sidebar.checkbox("Показывать выводы", True)
    inflation_enabled=st.sidebar.checkbox("Показывать график инфляции", True)

    research_objects = st.sidebar.multiselect(
        'Выберите исследование',
        ['образование',
        'строительство', 
        'здравоохранение'
        ],
        ['образование',
        'строительство', 
        'здравоохранение']
        )

    extra_research_auto_enabled=st.sidebar.checkbox('Корреляция продаж авто и реальной средней зп', True)
    extra_research_unemployment_enabled=st.sidebar.checkbox('Корреляция уровня безработицы и реальной средней зп', True)

    return {
        "inflation_enabled": inflation_enabled,
        "conclusions_enabled": conclusions_enabled,
        "industries": research_objects,
        "extra_research_auto_enabled": extra_research_auto_enabled,
        "extra_research_unemployment_enabled": extra_research_unemployment_enabled,
    }



if __name__ == "__main__":
    process_main_page()
