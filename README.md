# goodreadsAnaliticys

Etl para ler dados do goodreads de um deternimado usuário e salvar essas informaçãoe em um banco postgreel

Tabelas criadas no bando
1 - goodreads
    Tabela fato, com as informações básicas dos livros (título, autor, páginas, data início leitura, data fim leitura e etc)

2 - category
    Tabela dimensção,  chave: id_category 
                        1 - Lido
                        2 - Lendo 
                        3 - Quero Ler


3 - type
    Tabela dimensção, chave: id_type
                        1 - Biblioteca Física (criei um shelve para listar meus livros de minha biblioteca física env=URL_FISICOS)
                        2 - Kindle (tudo aquilo que não está na biblioteca física)