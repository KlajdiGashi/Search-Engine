from sqlalchemy import create_engine, text
import time
import statistics
# ALTER TABLE document MODIFY COLUMN content LONGTEXT;
db_config = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'port': '3310',
    'database': 'irproject'
}

database_uri = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
engine = create_engine(database_uri)

def measure_query_performance(query, runs=3):
    times = []
    for _ in range(runs):
        start_time = time.time()
        with engine.connect() as connection:
            result = connection.execute(text(query))
            result.fetchall()  # Fetch all results to ensure the query is fully executed
        end_time = time.time()
        times.append(end_time - start_time)
    return times

def explain_query(query):
    with engine.connect() as connection:
        result = connection.execute(text(f"EXPLAIN {query}"))
        return result.fetchall()

def create_index_if_not_exists(connection, index_name, table_name, index_query):
    result = connection.execute(text(f"SHOW INDEX FROM {table_name} WHERE Key_name = '{index_name}'"))
    if not result.fetchone():
        connection.execute(text(index_query))

def drop_index_if_exists(connection, index_name, table_name):
    result = connection.execute(text(f"SHOW INDEX FROM {table_name} WHERE Key_name = '{index_name}'"))
    if result.fetchone():
        connection.execute(text(f"DROP INDEX {index_name} ON {table_name}"))

def print_explain_results(explain_results):
    for row in explain_results:
        print(row)

def main():
    query = "SELECT * FROM document WHERE content LIKE '%homework%'"
    targeted_query = "SELECT * FROM document WHERE MATCH(content) AGAINST('homework' IN NATURAL LANGUAGE MODE)"

    with engine.connect() as connection:
        # Drop indexes if they exist
        drop_index_if_exists(connection, 'idx_title', 'document')
        drop_index_if_exists(connection, 'idx_content', 'document')

    print("Measuring performance...")
    times_before_index = measure_query_performance(query)
    explain_before_index = explain_query(query)

    with engine.connect() as connection:
        # Add indexes
        create_index_if_not_exists(connection, 'idx_title', 'document', 'CREATE INDEX idx_title ON document(title)')
        create_index_if_not_exists(connection, 'idx_content', 'document', 'CREATE FULLTEXT INDEX idx_content ON document(content)')

    times_after_index = measure_query_performance(targeted_query)
    explain_after_index = explain_query(targeted_query)

    avg_time_before_index = statistics.mean(times_before_index)
    avg_time_after_index = statistics.mean(times_after_index)

    print("\nAverage performance before indexing: {:.6f} seconds".format(avg_time_before_index))
    print("Query Execution Plan before indexing:")
    print_explain_results(explain_before_index)

    print("\nAverage performance after indexing: {:.6f} seconds".format(avg_time_after_index))
    print("Query Execution Plan after indexing:")
    print_explain_results(explain_after_index)
    
    improvement_percentage = ((avg_time_before_index - avg_time_after_index) / avg_time_before_index) * 100
    print("\nPerformance improvement after indexing: {:.2f}%".format(improvement_percentage))

if __name__ == "__main__":
    main()
