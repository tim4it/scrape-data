import logging
import time

import psycopg2
import scrapy

RETRY_DB_CONNECTION = 5
ESTATE_RECORDS_SIZE = 500

logger = logging.getLogger(__name__)


def try_db_connection():
    """
    Try to get connection to database with retry period
    :return: database connection
    """
    for i in range(0, RETRY_DB_CONNECTION):
        try:
            # Inside container reference to service postgres (yml), outside reference to localhost
            conn = psycopg2.connect(database="scrap_data",
                                    # host="localhost",
                                    host="postgres",
                                    user="postgres",
                                    password="postgres",
                                    port="5432")
            conn.cursor()
            return conn
        except psycopg2.Error as ex:
            logger.error(f"Wait for database connection! Sleep for one second! {ex}")
            time.sleep(1)
    raise psycopg2.DatabaseError(f"Error connecting to database, too many retries ({RETRY_DB_CONNECTION})!")


def clear_db_table(conn, cursor):
    """
    Remove all records in database table
    :param conn: database connection
    :param cursor:  cursor
    :return: nothing, we just clear items in the table
    """
    try:
        cursor.execute("TRUNCATE TABLE sreality")
        conn.commit()
    except psycopg2.Error as ex:
        logger.error(f"Error clearing database table! {ex}")


def count_records(cursor) -> int:
    """
    Get record count from database table - must be size of ESTATE_RECORDS
    :param cursor: database connection cursor
    :return: Record count from sreality table
    """
    try:
        cursor.execute("SELECT COUNT(*) from sreality")
        count = cursor.fetchone()
        return count[0]
    except psycopg2.Error as ex:
        logger.error(f"Error getting size of records! {ex}")


class SrealitySpider(scrapy.Spider):
    name = 'sreality'
    # For simplicity, we call all ESTATE_RECORDS_SIZE, no pagination, it is not necessary since this is a test
    start_urls = [f'https://www.sreality.cz/api/en/v2/estates?'
                  f'category_main_cb=1'
                  f'&category_type_cb=1'
                  f'&per_page={ESTATE_RECORDS_SIZE}']

    def parse(self, response, **kwargs):
        """
        Parse sreality.cz json data and store data to postgres database.
        Since HTML is created dynamically, we must call API with method GET and get ESTATE_RECORDS results from API.
        Also check if records are correctly inserted with quick count
        :param response: response data from API call - returned json format
        :return: no return, we just insert data to database one by one - bulk should be faster
        """
        try:
            # Get database connection and connection cursor
            conn = try_db_connection()
            cursor = conn.cursor()
            clear_db_table(conn, cursor)
            # Load json response data
            data = response.json()
            estates = data["_embedded"]["estates"]
            # Iterate over estates json list
            for estate in estates:
                img = estate["_links"]["image_middle2"][0]["href"]
                title = estate["name"]
                local_data = estate["locality"]
                price = estate["price"]
                cursor.execute("INSERT INTO sreality (title, local_data, img_href, price) "
                               "VALUES (%s, %s, %s, %s)",
                               (title, local_data, img, price))
            # Commit the changes - inserts to the database
            conn.commit()
            # Get count of inserted data records
            count = count_records(cursor)
            # Close the cursor and connection
            cursor.close()
            conn.close()
            # Check if database has ESTATE_RECORDS records - size
            assert count == ESTATE_RECORDS_SIZE
            logger.info(f"→  Inserted {count} records into database!")
            return None
        except psycopg2.Error as ex:
            logger.error(f"Error parsing/inserting/checking records! {ex}")
