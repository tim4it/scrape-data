import logging
import time

import psycopg2
import scrapy

logger = logging.getLogger(__name__)


def connect_to_db():
    """
    Get connection to database. If connection does not exist loop until it exists.
    Also remove all records in database table when database connection is valid
    :return: postgres connection
    """
    while True:
        try:
            # Inside container reference to service postgres, outside reference to localhost
            conn = psycopg2.connect(database="scrap_data",
                                    # host="localhost",
                                    host="postgres",
                                    user="postgres",
                                    password="postgres",
                                    port="5432")
            cursor = conn.cursor()
            cursor.execute("TRUNCATE TABLE sreality")
            conn.commit()
            return conn
        except psycopg2.Error as ex:
            logger.info(f"Wait for database initialization. Sleep for half a second! {ex}")
            time.sleep(0.5)


class SrealitySpider(scrapy.Spider):
    name = 'sreality'
    start_urls = ['https://www.sreality.cz/api/en/v2/estates?category_main_cb=1&category_type_cb=1&per_page=500']

    def parse(self, response, **kwargs):
        """
        Parse sreality.cz json data and store data to postgres database.
        Since HTML is created dynamically, we must call API with method GET and get 500 results from API
        :param response: response data -
        :return: insert database count data
        """
        # Wait for database connection
        conn = connect_to_db()
        cursor = conn.cursor()
        # Load json response data
        data = response.json()
        estates = data["_embedded"]["estates"]
        # iterate over estates json list
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
        # get count of inserted data
        cursor.execute("SELECT COUNT(*) from sreality")
        count = cursor.fetchone()
        # Close the cursor and connection
        cursor.close()
        conn.close()
        # Check if database has 500 records
        assert count[0] == 500
        logger.info(f"→  Inserted {count[0]} records into database!")
        return None
