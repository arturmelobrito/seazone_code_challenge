import pandas as pd
import pdb
from datetime import datetime
import matplotlib.pyplot as plt


def days_between(date1, date2):

    date1 = datetime.strptime(date1, '%Y-%m-%d %H:%M:%S')
    date2 = datetime.strptime(date2, '%Y-%m-%d')

    return abs((date2 - date1).days)

def is_weekend(date):
    
    n_week = datetime.strptime(date, '%Y-%m-%d').weekday()

    if n_week < 5:
        return False
    else:
        return True


#Ordena os bairros em ordem crescente de listings em um dicionário
def ordena_bairros_listings(df_details):

    dict_bairros = dict()

    list_of_details_rows = df_details.to_dict('records')

    #Preenche o dicionário com os bairros e a quantidade de ocorrências de cada
    for row in list_of_details_rows:

        if row['suburb'] not in dict_bairros:
            dict_bairros[row['suburb']] = 1

        else:
            dict_bairros[row['suburb']] += 1

    df_bairros = pd.DataFrame.from_dict(dict_bairros, orient = 'index')
    df_bairros.columns = ['Listings']
    df_bairros.rename_axis('Bairro', inplace=True)

    return df_bairros.sort_values(by = 'Listings')

#Ordena os bairros em ordem crescente de faturamento medio em um dicionario
def ordena_bairros_faturamento_medio(df_price, df_details):

    dict_bairros = dict()

    list_of_details_row = df_details.to_dict('records')
    list_of_price_row = df_price.to_dict('records')

    #Preenche o dicionario de bairros com o numero total de listings
    #junto com o faturamento total para determinado bairro
    for row in list_of_price_row:

        if row['occupied'] == 1:
            
            #Este FOR serve pra achar de qual bairro é o anúncio com ocupado = 1
            for row_2 in list_of_details_row:
                if row_2['airbnb_listing_id'] == row['airbnb_listing_id']:

                    if row_2['suburb'] not in dict_bairros:
                        dict_bairros[row_2['suburb']] = [1, row['price_string']]

                    else:
                        dict_bairros[row_2['suburb']][0] += 1
                        dict_bairros[row_2['suburb']][1] += row['price_string']


                    break

    #No lugar do faturamento total no bairro, substitui-se pelo
    #faturamento médio
    for bairro in dict_bairros:
        dict_bairros[bairro][1] = round(dict_bairros[bairro][1]/dict_bairros[bairro][0], 2)

    df_bairros = pd.DataFrame.from_dict(dict_bairros, orient = 'index')
    df_bairros.columns = ['Listings', 'Faturamento Médio']
    df_bairros.drop(['Listings'], axis = 1, inplace = True)
    df_bairros.rename_axis('Bairro', inplace=True)

    

    return df_bairros.sort_values(by = 'Faturamento Médio')


#Antecedência média das reservas
def antecedencia_media_listings(df_price):

    list_of_price_row = df_price.to_dict('records')

    listings = 0
    listings_fds = 0
    antecedencias = 0
    antecedencias_fds = 0


    for row in list_of_price_row:

        if row['occupied'] == 1:

            if is_weekend(row['date']):
                listings_fds += 1
                antecedencias_fds += days_between(row['booked_on'], row['date'])

            listings += 1
            antecedencias += days_between(row['booked_on'], row['date'])

    return antecedencias/listings, antecedencias_fds/listings_fds


def analise_listings(df_price, df_details):

    #Este dicionário tem as chaves como os faturamentos dos listings
    #e o valor de cada chave é uma lista da media de 5 caracteristicas
    #para aquele faturamento, na ordem:
    #[star_rating_, n_quartos, n_reviews, n_banheiros, listings_IDs_associados[], listings_totais]
    dict_properties = dict()

    list_of_price_row = df_price.to_dict('records')
    list_of_details_row = df_details.to_dict('records')

    #Cria as diferentes chaves para cada faturamento diferente
    for row in list_of_price_row:

        if row['price_string'] not in dict_properties:
            dict_properties[row['price_string']] = [0, 0, 0, 0, [row['airbnb_listing_id']], 0]

        else:
            if row['airbnb_listing_id'] not in dict_properties[row['price_string']][4]:

                dict_properties[row['price_string']][4].append(row['airbnb_listing_id'])


    #Preenche as caracteristicas de cada faturamento
    for row in list_of_details_row:

        for price in dict_properties:
            
            if row['airbnb_listing_id'] in dict_properties[price][4]:

                if pd.notna(row['star_rating']):
                    dict_properties[price][0] += row['star_rating']
                if pd.notna(row['number_of_bedrooms']):
                    dict_properties[price][1] += row['number_of_bedrooms']
                if pd.notna(row['number_of_reviews']):
                    dict_properties[price][2] += row['number_of_reviews']
                if pd.notna(row['number_of_bathrooms']):
                    dict_properties[price][3] += row['number_of_bathrooms']

                dict_properties[price][5] += 1

    for price in dict_properties:
        dict_properties[price][0] = round(dict_properties[price][0]/dict_properties[price][5], 1)
        dict_properties[price][1] = round(dict_properties[price][1]/dict_properties[price][5])
        dict_properties[price][2] = round(dict_properties[price][2]/dict_properties[price][5])
        dict_properties[price][3] = round(dict_properties[price][3]/dict_properties[price][5])


    df_properties_by_price = pd.DataFrame.from_dict(dict_properties, orient = 'index')
    df_properties_by_price = df_properties_by_price.drop([4,5], axis = 1)
    df_properties_by_price.columns = ['Estrelas', 'Quartos', 'Reviews', 'Banheiros']
    df_properties_by_price.rename_axis('Preço', inplace=True)
    df_properties_by_price.sort_index(inplace = True)

    axs = df_properties_by_price.plot.area(figsize=(12, 4), subplots=True)
    plt.show()

    return 0

            


def main():

    df_price = pd.read_csv("desafio_priceav(1)(2).csv")
    df_details = pd.read_csv("desafio_details(1)(2).csv")


    #1 - Bairros ordenados por número de listings
    bairros_ordenados_listings = ordena_bairros_listings(df_details)
    print(bairros_ordenados_listings)
    print("\n\n")

    #2 - Bairros ordenados por faturamento medio
    bairros_ordenados_faturamento_medio = ordena_bairros_faturamento_medio(df_price, df_details)
    print(bairros_ordenados_faturamento_medio)
    print("\n\n")

    #3 - Análise do faturamento do anúncio com suas características
    execucao = analise_listings(df_price, df_details)

    #4 - Antecedencia Média dos Listings
    antecedencia_media, antecedencia_media_fds = antecedencia_media_listings(df_price)

    print("Antecedência média:", round(antecedencia_media), "dias")
    print("Antecedência média para finais de semana:", round(antecedencia_media_fds), "dias")

    if antecedencia_media_fds > antecedencia_media:
        print("Antecedência média é maior para finais de semana.")
    else:
        print("Antecedência média geral é maior.")

    return 0

main()
