import sqlite3
from mcp.server.fastmcp import FastMCP

# Inicjalizacja serwera MCP o nazwie "sql-agent"
mcp = FastMCP("SQL-Agent-Server")
DB_PATH = "northwind.db"  # upewnij się, że setup_db.py już się wykonał

@mcp.tool()
def get_db_schema() -> str:
    """Zwraca listę tabel, ich kolumn oraz opis relacji w bazie Northwind."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    
    schema_info = []
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [f"{col[1]} ({col[2]})" for col in cursor.fetchall()]
        schema_info.append(f"Tabela: {table}\nKolumny: {', '.join(columns)}\n")
    
    conn.close()
    
    # --- TUTAJ DODAJEMY PODPOWIEDŹ BIZNESOWĄ DLA LLM ---
    business_context = (
        "\n=== WSKAZÓWKI DOTYCZĄCE RELACJI (Klucze obce) ===\n"
        "- Aby połączyć zamówienie z produktami i poznać ich nazwy lub ilości, MUSISZ połączyć TRZY tabele:\n"
        "  `Orders` JOIN `OrderDetails` ON Orders.OrderID = OrderDetails.OrderID\n"
        "  `OrderDetails` JOIN `Products` ON OrderDetails.ProductID = Products.ProductID\n"
        "- Tabela `Orders` zawiera daty (`OrderDate`), ale NIE zawiera nazw ani ilości produktów.\n"
        "- Tabela `OrderDetails` zawiera ilości (`Quantity`) i ceny, ale NIE zawiera nazw produktów ani dat.\n"
        "- Tabela `Products` zawiera nazwy produktów (`ProductName`).\n"
        "- Jeśli szukasz pracowników, użyj tabeli `Employees`. Jeśli klientów: `Customers`.\n"
    )
    
    return "\n".join(schema_info) + business_context

@mcp.tool()
def run_sql_query(query: str) -> str:
    """Wykonuje bezpieczne zapytanie SQL SELECT na bazie Northwind i zwraca wyniki jako tekst."""
    # Blokada bezpieczeństwa przed modyfikacją bazy danych
    if any(keyword in query.upper() for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]):
        return "Błąd: Dozwolone są tylko zapytania typu SELECT (odczyt danych)!"
        
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Pobranie nazw kolumn dla czytelności wyniku
        columns = [description[0] for description in cursor.description]
        conn.close()
        
        # Formatowanie wyniku do czytelnego stringa
        result = [f"Kolumny: {', '.join(columns)}"]
        for row in rows:
            result.append(", ".join(str(val) for val in row))
        return "\n".join(result)
    except Exception as e:
        return f"Błąd podczas wykonywania SQL: {str(e)}"

if __name__ == "__main__":
    # Uruchomienie serwera MCP w trybie developerskim (nasłuchuje na standardowym wejściu/wyjściu)
    mcp.run()