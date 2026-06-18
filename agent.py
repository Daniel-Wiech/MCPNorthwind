import asyncio
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Konfiguracja uruchamiania serwera MCP
server_params = StdioServerParameters(
    command="poetry",
    args=["run", "python", "server.py"],
)

async def main():
    print("🤖 Uruchamianie Agenta SQL z MCP (Wersja Liniowa)...")
    
    # Inicjalizacja modelu
    llm = ChatOllama(model="llama3.1", temperature=0)

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            mcp_tools = await session.list_tools()
            print(f"✅ Połączono z serwerem MCP. Narzędzia: {[t.name for t in mcp_tools.tools]}")

            # 1. Uniwersalny system prompt
            system_prompt = (
                "Jesteś rygorystycznym i hiper-dokładnym robotem SQL pracującym na bazie SQLite.\n"
                "Twoim celem jest wygenerowanie poprawnego zapytania SQL na podstawie przekazanego schematu.\n"
                "\n"
                "Zanim napiszesz zapytanie SQL, MUSISZ przeprowadzić wewnętrzną analizę (krok po kroku):\n"
                "1. Znajdź w schemacie tabele, które są niezbędne do udzielenia odpowiedzi.\n"
                "2. Dla KAŻDEJ wybranej tabeli, dosłownie PRZECZYTAJ i wypisz listę dostępnych w niej kolumn.\n"
                "3. Upewnij się, że kolumny, których chcesz użyć w sekcjach SELECT, WHERE, JOIN oraz GROUP BY, FIZYCZNIE ISTNIEJĄ w tych tabelach w schemacie.\n"
                "4. Jeśli łączysz tabele (JOIN), sprawdź dwukrotnie, czy łączysz je po kluczach, które faktycznie są wymienione w obu tabelach.\n"
                "\n"
                "ZASADY SKŁADNI SQLITE:\n"
                "- Jeśli nazwa tabeli zawiera spacje, weź ją w nawiasy kwadratowe (np. `[Nazwa Tabeli]`).\n"
                "- Jeśli tworzysz alias kolumny (AS), używaj wyłącznie jednej zrastanej nazwy lub podkreślników, np. `AS LiczbaZamowien` lub `AS Liczba_Zamowien`. NIGDY nie stawiaj tam spacji!\n"
                "- Do filtracji lat i miesięcy z dat tekstowych (YYYY-MM-DD) używaj wyłącznie operatora `LIKE '2012%'`.\n"
                "- Zwróć wyłącznie czysty kod SQL w znacznikach ```sql ... ```, bez żadnych innych komentarzy."
            )

            # Twoje nowe zapytanie użytkownika
            #user_query = "Zrób mi listę pracowników zatrudnionych w 2012 roku i napisz mi z jakich miast oni są"
            user_query = "Zrób mi listę pracowników którzy sprzedali najwięcej zamówień"
            print(f"\n👤 Użytkownik: {user_query}\n")

            # --- KROK 1: Pytamy o schemat bazy ---
            print("🛠️ KROK 1: Pobieranie struktury bazy danych...")
            result_schema = await session.call_tool("get_db_schema", arguments={})
            schema_context = result_schema.content[0].text
            
            # --- KROK 2: Generowanie i uruchomienie zapytania SQL ---
            print("🧠 KROK 2: Model analizuje schemat i tworzy zapytanie SQL...")
            
            prompt_for_sql = (
                f"{system_prompt}\n\n"
                f"Oto schemat bazy danych:\n{schema_context}\n\n"
                f"Na podstawie powyższego schematu stwórz JEDNO zapytanie SQL, które odpowie na pytanie: {user_query}.\n"
                f"⚠️ BEZWZGLĘDNA ZASADA: Do tabeli Employees użyj wyłącznie konkretnych kolumn: FirstName, LastName, Title, HireDate.\n"
                f"NIGDY NIE używaj gwiazdki (*) i NIGDY nie pobieraj kolumny 'Photo', bo zawiera uszkodzone dane binarne.\n"
                f"Zwróć WYŁĄCZNIE czysty kod SQL, bez żadnego dodatkowego tekstu."
            )
            
            response_sql = llm.invoke([HumanMessage(content=prompt_for_sql)])
            sql_query = response_sql.content.strip().replace("```sql", "").replace("```", "").strip()
            
            print(f"🖥️ Wygenerowane zapytanie SQL:\n{sql_query}")
            
            # Wykonanie zapytania na serwerze MCP
            print("\n🛠️ KROK 3: Uruchamianie zapytania w bazie danych...")
            try:
                result_db = await session.call_tool("run_sql_query", arguments={"query": sql_query})
                db_output = result_db.content[0].text
            except Exception as e:
                db_output = f"Błąd wykonania zapytania: {str(e)}"
            
            print(f"📥 Dane zwrócone z bazy:\n{db_output}")

            # --- KROK 3: Generowanie raportu końcowego ---
            print("\n🧠 KROK 4: Generowanie ostatecznego raportu...")
            prompt_for_report = (
                f"Jesteś analitykiem. Na podstawie pytania: '{user_query}' "
                f"oraz prawdziwych danych z bazy:\n{db_output}\n"
                f"Przygotuj czytelny, ładny raport po polsku w formacie Markdown (użyj tabeli).\n"
                f"Pisz wyłącznie prawdę, nie zmyślaj żadnych nazwisk ani dat."
            )
            
            final_report = llm.invoke([HumanMessage(content=prompt_for_report)])
            
            print("\n📊 --- RAPORT KOŃCOWY --- 📊\n")
            print(final_report.content)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())