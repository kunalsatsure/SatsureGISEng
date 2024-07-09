# Import necessary libraries
import pandas as pd
from os import path
from multiprocessing import Process, Semaphore
import logging
import psycopg2 as pg

# Configuration
district_id = ['27']  # List of district IDs for which data needs to be fetched
output_path = r"C:\Users\Satsure\Downloads\drive-download"
logging.basicConfig(filename='Not Matched Scrapped.log', level=logging.INFO, format='%(asctime)s-[%(levelname)s] %(message)s')

def fetch_data(dist_id, tablename, semaphore):
    '''
    Fetch data from PostgreSQL database for a given district ID.
    
    Parameters:
    - dist_id: District ID (string)
    - tablename: Name of the table to query (string)
    - semaphore: Semaphore for controlling concurrent access (Semaphore object)
    
    Output:
    - CSV file containing fetched data
    - Logging information about the fetch operation
    '''
    with semaphore:
        try:
            print(f"Entered function for district ID: {dist_id}")
            query = f"""
                    SELECT DISTINCT district_id, tehsil_id, village_id, district, tehsil, village 
                    FROM {tablename} 
                    WHERE district_id = '{dist_id}'
                    """
            
            # Establish database connection
            conn = pg.connect(database="", user="", password="", host="")
            queriedData = pd.read_sql_query(query, con=conn)
            conn.close()

            # Save queried data to CSV file
            if queriedData is not None:
                queriedData.to_csv(path.join(output_path, f'Distinct Records_id_{dist_id}.csv'), encoding='utf-8', index=False)
            logging.info(f'Record count for district ID {dist_id}: {len(queriedData) if queriedData is not None else 0}')

        except Exception as e:
            print(f"Error occurred for district ID {dist_id}: {e}")
            logging.error(f"Error occurred for district ID {dist_id}: {e}")

# Main process
if __name__ == '__main__':
    semaphore = Semaphore(4)  # Limit concurrent processes to 4
    table_name = 'rajasthan_d1_complete_new'
    processes = [Process(target=fetch_data, args=(dis_id, table_name, semaphore)) for dis_id in district_id]

    # Start processes
    for process in processes:
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()
