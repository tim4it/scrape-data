#!/usr/bin/python3
import logging
import sys
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer

import psycopg2

from sreality_scraper.spiders.sreality import ESTATE_RECORDS_SIZE, RETRY_DB_CONNECTION, try_db_connection

HOST_NAME = "0.0.0.0"
PORT = 8080

logger = logging.getLogger(__name__)


def read_html_template(path):
    """
    Read HTML file from template directory/path
    :param path to html template
    """
    try:
        with open(path) as f:
            file = f.read()
    except Exception as ex:
        logger.error(f"Error loading html template! {ex}")
    return file


def get_scraped_records():
    """
    Get all records from sql statement. Since we need to wait for connection and record fill, we do it safely
    :return: all records from database
    """
    for i in range(0, RETRY_DB_CONNECTION):
        try:
            conn = try_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT s.title, s.local_data, s.price, s.img_href FROM sreality s")
            records = cursor.fetchall()
            # Close the cursor and connection
            cursor.close()
            conn.close()
            if len(records) >= ESTATE_RECORDS_SIZE:
                return records
            else:
                raise psycopg2.Error("Records are not filled yet!")
        except psycopg2.Error as ex:
            logger.error(f"Wait for database records to be filled! Sleep for one second! {ex}")
            time.sleep(1)
    raise psycopg2.Error(f"Error getting records from database, too many retries ({RETRY_DB_CONNECTION})!")


class PythonServer(SimpleHTTPRequestHandler):
    """
    Python HTTP Server that handles GET requests - request handler
    """

    def do_GET(self):
        """
        GET request from html simple dynamic template
        """
        if self.path == '/':
            self.path = './templates/show_records.html'
            self._show_records()

    def _show_records(self):
        """
        Load html template and replace template html table rows with data from database
        """
        try:
            file = read_html_template(self.path)
            # fetch records from database
            table_data = get_scraped_records()
            table_row = ""
            for index, data in enumerate(table_data):
                table_row += "<tr>"
                table_row += f'<td style="width:15px"><b>{index + 1}</b></td>'
                for idx, item in enumerate(data):
                    if (len(data) - 1) == idx:
                        table_row += '<td style="width:400px;text-align:center">'
                        table_row += f'<img src="{str(item)}">'
                    else:
                        table_row += "<td>"
                        table_row += str(item)
                    table_row += "</td>"
                table_row += "</tr>"
            # replace {{ estate_size }} and {{ estate_records }} in template by table_row
            file = file.replace("{{ estate_size }}", str(ESTATE_RECORDS_SIZE)) \
                .replace("{{ estate_records }}", table_row)
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write(bytes(file, "utf-8"))
        except Exception as ex:
            logger.error(f"Error creating dynamic html template! {ex}")


if __name__ == "__main__":
    logger.info(f"→  Server started at http://{HOST_NAME}:{PORT}")
    server = HTTPServer((HOST_NAME, PORT), PythonServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped!")
        server.server_close()
        sys.exit(0)
