#!/usr/bin/python3
import sys
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer

import psycopg2

HOST_NAME = "0.0.0.0"
PORT = 8080


def get_scraped_records():
    """
    Get all records from sql statement
    :return: all records from database
    """
    while True:
        try:
            conn = psycopg2.connect(database="scrap_data",
                                    host="postgres",
                                    user="postgres",
                                    password="postgres",
                                    port="5432")
            cursor = conn.cursor()
            cursor.execute("SELECT s.title, s.local_data, s.price, s.img_href FROM sreality s")
            records = cursor.fetchall()
            # Close the cursor and connection
            cursor.close()
            conn.close()
            if len(records) > 100:
                return records
            else:
                raise psycopg2.Error("We don't have records yet!")
        except psycopg2.Error as ex:
            print(f"Wait for database records. Sleep for one second! {ex}")
            time.sleep(1)


def read_html_template(path):
    """Read HTML file from template"""
    try:
        with open(path) as f:
            file = f.read()
    except Exception as e:
        file = e
    return file


def show_records(self):
    """function to show records in template"""
    file = read_html_template(self.path)
    # fetch records from database
    table_data = get_scraped_records()
    table_row = ""
    for data in table_data:
        table_row += "<tr>"
        for idx, item in enumerate(data):
            if (len(data) - 1) == idx:
                table_row += '<td style="width:400px;text-align:center">'
                table_row += f'<img src="{str(item)}">'
            else:
                table_row += "<td>"
                table_row += str(item)
            table_row += "</td>"
        table_row += "</tr>"
    # replace {{user_records}} in template by table_row
    file = file.replace("{{user_records}}", table_row)
    self.send_response(200, "OK")
    self.end_headers()
    self.wfile.write(bytes(file, "utf-8"))


class PythonServer(SimpleHTTPRequestHandler):
    """Python HTTP Server that handles GET requests"""

    def do_GET(self):
        if self.path == '/':
            self.path = './templates/show_records.html'
            # call show_records function to show users entered
            show_records(self)


if __name__ == "__main__":
    print(f"→  Server started at http://{HOST_NAME}:{PORT}")
    server = HTTPServer((HOST_NAME, PORT), PythonServer)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped!")
        server.server_close()
        sys.exit(0)
