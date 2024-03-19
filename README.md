# goodreadsAnalytics

## Descrição
Este é um projeto ETL (Extract, Transform, Load) para ler dados do Goodreads de um determinado usuário e salvar essas informações em um banco de dados PostgreSQL.

## Tabelas Criadas no Banco de Dados

### Tabela 1: goodreads (Tabela Fato)
Esta tabela contém as informações básicas dos livros, como título, autor, número de páginas, data de início de leitura, data de término de leitura, etc.

### Tabela 2: category (Tabela Dimensão)
Esta tabela é uma dimensão que contém as categorias de leitura. A chave é id_category e os valores possíveis são:
- 1: Lido
- 2: Lendo
- 3: Quero Ler

### Tabela 3: type (Tabela Dimensão)
Esta tabela é uma dimensão que contém os tipos de livro. A chave é id_type e os valores possíveis são:
- 1: Biblioteca Física (Criei uma shelve (no goodreads) para listar meus livros de minha biblioteca física env=URL_FISICOS)
- 2: Kindle (tudo aquilo que não está na biblioteca física)

## Referências
- [Goodreads](https://www.goodreads.com/)
- [PostgreSQL](https://www.postgresql.org/)
