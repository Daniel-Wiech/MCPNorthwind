# SQL Agent z MCP, Ollama i SQLite

Agent AI wykorzystujący **LangChain**, **Ollama**, **Model Context Protocol (MCP)** oraz bazę danych **SQLite (Northwind)** do automatycznego generowania, wykonywania i raportowania zapytań SQL w języku naturalnym.

## Architektura rozwiązania

```text
┌──────────────┐
│ Użytkownik   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│   agent.py   │
│ LangChain +  │
│   Ollama     │
└──────┬───────┘
       │ MCP
       ▼
┌──────────────┐
│  server.py   │
│ MCP Server   │
└──────┬───────┘
       │ SQLite
       ▼
┌──────────────┐
│ northwind.db │
└──────────────┘
```

## Opis działania

Projekt składa się z dwóch głównych komponentów:

### Agent (`agent.py`)

Agent:

1. Łączy się z lokalnym modelem LLM uruchomionym w Ollama.
2. Pobiera schemat bazy danych z serwera MCP.
3. Przekazuje schemat do modelu.
4. Generuje poprawne zapytanie SQL.
5. Wysyła zapytanie do serwera MCP.
6. Odbiera wyniki.
7. Tworzy raport końcowy w formacie Markdown.

### Serwer MCP (`server.py`)

Serwer udostępnia dwa narzędzia:

#### `get_db_schema`

Zwraca:

* listę tabel,
* kolumny tabel,
* wskazówki dotyczące relacji między tabelami.

#### `run_sql_query`

Wykonuje zapytania SQL typu:

```sql
SELECT ...
```

Dodatkowo blokuje operacje modyfikujące bazę danych:

* DROP
* DELETE
* UPDATE
* INSERT
* ALTER

Dzięki temu agent ma wyłącznie dostęp do odczytu danych.

---

# Technologie

* Python 3.11+
* Poetry
* LangChain
* LangChain Ollama
* MCP (Model Context Protocol)
* SQLite
* Ollama
* Docker

---

# Struktura projektu

```text
.
├── agent.py
├── server.py
├── northwind.db
├── pyproject.toml
├── poetry.lock
├── docker-compose.yml
└── README.md
```

---

# Wymagania

Przed uruchomieniem należy posiadać:

* Docker
* Docker Compose
* Python 3.11+
* Poetry

---

# Instalacja Ollama

Uruchom kontener:

```bash
docker-compose up -d
```

Sprawdź czy kontener działa:

```bash
docker ps
```

Powinien być widoczny kontener:

```text
ollama_mcp
```

---

# Pobranie modelu

Po uruchomieniu Ollama pobierz model:

```bash
docker exec -it ollama_mcp ollama run llama3.1
```

Model zostanie zapisany w wolumenie Dockera i będzie dostępny lokalnie pod adresem:

```text
http://localhost:11434
```

---

# Instalacja zależności

Instalacja projektu przez Poetry:

```bash
poetry install
```

Aktywacja środowiska:

```bash
poetry shell
```

lub uruchamianie komend przez:

```bash
poetry run
```

---

# Konfiguracja bazy danych

W katalogu projektu umieść plik:

```text
northwind.db
```

Domyślna ścieżka wykorzystywana przez serwer:

```python
DB_PATH = "northwind.db"
```

---

# Uruchomienie projektu

Uruchom agenta:

```bash
poetry run python agent.py
```

Agent automatycznie:

1. Uruchomi serwer MCP.
2. Pobierze schemat bazy danych.
3. Wygeneruje SQL.
4. Wykona zapytanie.
5. Wygeneruje raport końcowy.

---

# Przykładowe zapytania

W pliku `agent.py` można zmieniać treść:

```python
user_query = "Zrób mi listę pracowników którzy sprzedali najwięcej zamówień"
```

Przykłady:

```python
user_query = "Pokaż 10 najlepiej sprzedających się produktów"
```

```python
user_query = "Którzy pracownicy zostali zatrudnieni w 2012 roku?"
```

```python
user_query = "Jaki klient złożył najwięcej zamówień?"
```

```python
user_query = "Ile produktów sprzedano w 2014 roku?"
```

---

# Przepływ działania

## Krok 1

Agent pobiera schemat bazy:

```text
get_db_schema()
```

## Krok 2

Model analizuje:

* tabele,
* kolumny,
* relacje.

Generowany jest SQL.

Przykład:

```sql
SELECT
    Employees.FirstName,
    Employees.LastName,
    COUNT(Orders.OrderID) AS Liczba_Zamowien
FROM Employees
JOIN Orders
    ON Employees.EmployeeID = Orders.EmployeeID
GROUP BY
    Employees.FirstName,
    Employees.LastName
ORDER BY
    Liczba_Zamowien DESC;
```

## Krok 3

SQL trafia do:

```text
run_sql_query()
```

i zostaje wykonany na SQLite.

## Krok 4

Model generuje raport końcowy:

```markdown
| Imię | Nazwisko | Liczba zamówień |
|-------|----------|----------------|
| Nancy | Davolio | 123 |
| Andrew | Fuller | 115 |
```

---

# Bezpieczeństwo

Serwer MCP blokuje operacje modyfikujące bazę danych:

```python
["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]
```

Dzięki temu agent nie może:

* usuwać danych,
* modyfikować rekordów,
* zmieniać struktury tabel.

Dozwolone są wyłącznie zapytania odczytujące dane.

---

# Możliwe rozszerzenia

* Obsługa wielu baz danych.
* Obsługa PostgreSQL.
* Obsługa Microsoft SQL Server.
* Automatyczne retry przy błędach SQL.
* Walidacja wygenerowanego SQL.
* Interfejs webowy (FastAPI + Streamlit).
* Obsługa wielu modeli Ollama.
* Integracja z OpenAI API.
* Integracja z Azure OpenAI.

---

# Autor

Projekt demonstracyjny pokazujący wykorzystanie:

* MCP (Model Context Protocol)
* LangChain
* Ollama
* SQLite
* Agentów AI generujących SQL na podstawie języka naturalnego

---

# Przykładowe działanie

<img width="739" height="570" alt="image" src="https://github.com/user-attachments/assets/8a6f62c9-fb24-452a-ae13-e93f9886bd91" />

<img width="628" height="792" alt="testdzialania1" src="https://github.com/user-attachments/assets/50b9a93c-4db2-4757-8b3f-5f8e35faa61a" />


