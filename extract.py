from bs4 import BeautifulSoup
import re
import requests
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine,text
import os
import pandas as pd

# Carrega as variáveis de ambiente
load_dotenv()

meses = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
    'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}

def getData(txt):
    if txt != 'not set':
        year = re.findall("([0-9]{4})",txt)[0]
        month = txt[:3]
        day_ext = re.findall(" (.*?),",txt)

        if day_ext:
            day = day_ext[0]
        else:
            day = 1

        return datetime(int(year), meses[month], int(day))
    else:
        return 'not set'

def getLivrosFisicos():
    url_fisico = "https://www.goodreads.com/review/list/90257929?shelf=biblioteca-fisica&page="
    page = 1

    biblioteca_ficica=[]
    while True:
        html = requests.get(url_fisico+str(page)).content
        soup = BeautifulSoup(html, 'html.parser')
        html_table = soup.select("#booksBody > tr")

        if html_table:
            page=page+1
            for l in html_table:
                biblioteca_ficica.append(l['id'])
        else:
            break
    return biblioteca_ficica
          
def getAll():
    df = pd.DataFrame()
    listaLivrosfisicos = getLivrosFisicos()
    url_all = "https://www.goodreads.com/review/list/90257929?shelf=%23ALL%23&page="
    page = 1

    while True:
        html = requests.get(url_all+str(page)).content
        soup = BeautifulSoup(html, 'html.parser')

        html_table = soup.select("#booksBody > tr")

        if html_table:
            page=page+1
            for l in html_table:
                ext_linha = l['id']
                ext_title = l.select("td.field.title > div > a ")[0]['title']
                ext_colecao_geral = re.findall("\\((.*?)\\)", ext_title)
                ext_author = re.search(">(.*?)</a>",  str( l.select("td.field.author > div > a"))).group(1)
                ext_pages =  re.findall("([,0-9]{1,5})",str( l.select("td.field.num_pages > div > nobr")))
                ext_pub =  re.findall("([0-9]{4})",str( l.select("td.field.date_pub > div ")[0]))
                ext_pub_edit = re.findall("([0-9]{4})",str( l.select("td.field.date_pub_edition > div ")[0]))
                ext_rating = re.findall("title=(.*?)><span class=", str(l.select("td.field.rating > div > span")[0]))
                ext_added = l.select("td.field.date_added > div > span ")[0]['title']

                ext_started = l.select("td.field.date_started > div")
                list_started = re.findall(">(.*?)</span>",str( ext_started) )

                ext_read = l.select("td.field.date_read > div")
                list_read = re.findall(">(.*?)</span>",str( ext_read) )

                #Verifica se pagina não é desconhecida
                if ext_pages:
                    tra_pages=ext_pages[0]
                else:
                    tra_pages=0                

                #Verifica se existe ano de publicação, caso não exista usa ano de publicação da edição
                if ext_pub:
                    tra_pub=ext_pub[0]
                elif ext_pub_edit:
                    tra_pub=ext_pub_edit[0]
                else:        
                    tra_pub="na"

                #trata não lidos/avaliados
                if ext_rating:        
                    tra_rating = ext_rating[0]
                else:            
                    tra_rating = "na"

                #Extraindo do titulo a coleção e numero da sequencia
                if ext_colecao_geral:
                    ext_colecao= re.sub("[0-9]","",ext_colecao_geral[0])
                    ext_num_colecao = re.findall("([0-9]{1,2})",ext_colecao_geral[0])
                    if ext_num_colecao:
                        tra_num_colecao = ext_num_colecao[0]
                    else:
                        tra_num_colecao = 1
                else:
                    ext_colecao = "na"
                    tra_num_colecao = "na"

                #verifica se livro é fisico ou kindle
                if ext_linha in listaLivrosfisicos:
                    tra_tipo = 'Fisico'
                else:
                    tra_tipo = 'kindle'

                #for para mais de 1 litura em um mesmo livro
                ic=0
                for lista in list_started:

                    if getData(list_read[ic]) != 'not set':
                        tra_categoria = 'Lido'
                    elif getData(lista) != 'not set':
                        tra_categoria = 'Lendo'
                    else:
                        tra_categoria = 'Quero Ler'
                    

                    data = [{'title': ext_title, 'category': tra_categoria, 'type': tra_tipo}]
                    df = pd.concat([df, pd.DataFrame.from_dict(data)], ignore_index=True)
                    ic=ic+1
      
        else:
            break

    print(df.head())  
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)
    df.to_sql('goodreads', con=engine, if_exists='replace', index=False)

def teste():
    DATABASE_URL = os.getenv("DATABASE_URL")
    engine = create_engine(DATABASE_URL)    
    with engine.connect() as conn:
    # Follow the identifier quoting convention for your RDBMS
    # to avoid problems with mixed-case names.
        conn.execute(text("""
                      DROP TABLE "goodreads" 
                      """))
        # Commit if necessary
        conn.commit()    

#getAll()
#ext_title
#ext_colecao_geral
#ext_colecao
#tra_num_colecao
#ext_author
#tra_pages
#tra_pub
#tra_rating
#getData(ext_added)
#getData(lista)
#getData(list_read[ic])
#tra_tipo
#tra_categoria

if __name__ == "__main__":
    #getAll()
    teste()
