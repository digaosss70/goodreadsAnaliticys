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

rating = {
        '"did not like it"':1,
        '"it was ok"':2,
        '"liked it"':3,
        '"really liked it"':4,
        '"it was amazing"':5
        }

def postgreesql():
    DATABASE_URL = os.getenv("DATABASE_URL")
    return create_engine(DATABASE_URL)

def iniciaTabelas():
    engine = postgreesql()
    with engine.connect() as conn:

        #Cria tabela fato goodreads caso não exista
        conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS goodreads (
                                title varchar,
                                colection varchar,
                                seq_colection int,	
                                id_category int not null,
                                id_type int not null,
                                author varchar,
                                pages int,
                                id_rating int,
                                added date,
                                read date,
                                start date,
                                pub_year int
                            ); 
                      """))
        #Cria tabela dimensão tipo (kindle, biblioteca fisica) e inseri dimensões
        conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS type (
                                id_type int PRIMARY KEY,
                                type varchar
                                );
                            INSERT INTO type (id_type, type) VALUES (1,'Biblioteca Física'),(2,'kindle')
                                ON CONFLICT (id_type) DO NOTHING;                    
                        """))
        #Cria tabela dimensão category (lido, lendo, quero ler)
        conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS category (
                                id_category int PRIMARY KEY,
                                category varchar
                                );
                            INSERT INTO category (id_category, category) VALUES (1,'Lido'),(2,'Lendo'),(3,'Quero Ler')
                                ON CONFLICT (id_category) DO NOTHING;                  
                        """))
        #truncate table goodreads limpa tabela goodreads
        conn.execute(text("""
                          truncate goodreads ;
                          """))
        #Log de atualizações 
        conn.execute(text("""
                            CREATE TABLE IF NOT EXISTS log_insert (
                                insert_date DATE PRIMARY KEY,
                                insert_time varchar,
                                insert_qtd INT
                            );
                          """))                       
        # Commit if necessary
        conn.commit()    
    
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
        return 'null'          

def getLivrosFisicos():
    url_fisico = os.getenv("URL_FISICOS")
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
    iniciaTabelas()
    contador = 0
    engine = postgreesql()    
    insert = "insert  into  goodreads  (title, colection, seq_colection,id_category,id_type,author,pages,id_rating,added,read,start,pub_year) values "
    listaLivrosfisicos = getLivrosFisicos()
    url_all = os.getenv("URL_ALL")
    page = 1

    while True:
        html = requests.get(url_all+str(page)).content
        soup = BeautifulSoup(html, 'html.parser')

        html_table = soup.select("#booksBody > tr")

        if html_table:
            page=page+1
            for l in html_table:
                ext_linha = l['id']
                ext_title =  f"{l.select("td.field.title > div > a ")[0]['title'].replace("'","")}"
                ext_colecao_geral = re.findall("\\((.*?)\\)", ext_title)
                ext_author = f"{re.search(">(.*?)</a>",  str( l.select("td.field.author > div > a"))).group(1).replace("'","")}"
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
                    tra_pages=int(ext_pages[0].replace(",",""))
                else:
                    tra_pages='null'                

                #Verifica se existe ano de publicação, caso não exista usa ano de publicação da edição
                if ext_pub:
                    tra_pub=ext_pub[0]
                elif ext_pub_edit:
                    tra_pub=ext_pub_edit[0]
                else:        
                    tra_pub='null'

                #trata não lidos/avaliados
                if ext_rating:        
                    tra_rating = rating[ext_rating[0]]
                else:            
                    tra_rating = 'null'

                #Extraindo do titulo a coleção e numero da sequencia
                if ext_colecao_geral:
                    ext_colecao= f"'{re.sub("[0-9]","",ext_colecao_geral[0])}'"
                    ext_num_colecao = re.findall("([0-9]{1,2})",ext_colecao_geral[0])
                    if ext_num_colecao:
                        tra_num_colecao = ext_num_colecao[0]
                    else:
                        tra_num_colecao = 1
                else:
                    ext_colecao = 'null'
                    tra_num_colecao = 'null'

                #verifica se livro é fisico ou kindle
                if ext_linha in listaLivrosfisicos:
                    tra_tipo = 1#'Fisico'
                else:
                    tra_tipo = 2#'kindle'

                #for para mais de 1 litura em um mesmo livro
                ic=0
                for lista in list_started:

                    if getData(list_read[ic]) != 'null':
                        tra_categoria = 1 #'Lido'
                    elif getData(lista) != 'null':
                        tra_categoria = 2 #'Lendo'
                    else:
                        tra_categoria = 3#'Quero Ler'
                    

                    if getData(ext_added) != 'null':
                        load_added = f"'{getData(ext_added)}'"
                    else:
                        load_added ='null'

                    if getData(list_read[ic]) != 'null':
                        load_read = f"'{getData(list_read[ic])}'"
                    else:
                        load_read ='null'    

                    if getData(lista) != 'null':
                        load_start = f"'{getData(lista)}'"
                    else:
                        load_start ='null'

                    query = f"('{ext_title}',{ext_colecao},{tra_num_colecao},{tra_categoria},{tra_tipo},'{ext_author}',{tra_pages},{tra_rating},{load_added},{load_read},{load_start},{tra_pub}),"
                    insert = insert + query
                    
                    ic=ic+1
                    contador=contador+1
      
        else:
            break

    query = insert[:-1]+";"
    engine = postgreesql()
    insert_date = datetime.now().strftime('%Y-%m-%d')git
    insert_time = datetime.now().strftime('%H:%M:%S')

    with engine.connect() as conn:
        conn.execute(text(query))
        conn.execute(text(f"INSERT INTO log_insert (insert_date,insert_time, insert_qtd) VALUES ('{insert_date}','{insert_time}', {contador}) ON CONFLICT (insert_date) DO UPDATE SET insert_qtd = EXCLUDED.insert_qtd , insert_time = EXCLUDED.insert_time;"))
        conn.commit()

    return f"Em {insert_date} as {insert_time} foram inseridos {contador} Registros!"

if __name__ == "__main__":
    getAll()
