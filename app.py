from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
from sqlalchemy import create_engine, text
import logging
import random

# Create SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Set default configurations
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # This is initially set to SQLite

    # Initialize SQLAlchemy with the Flask app
    db.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/connect', methods=['POST'])
    def connect():
        data = request.get_json()  # Get JSON data
        server_ip = data.get('server-ip')
        db_name = data.get('db-name')
        username = data.get('username')
        password = data.get('password')

        # Check if all required fields are provided
        if not (server_ip and db_name and username or password):
            return jsonify(message="All fields are required."), 400

        # Dynamically set the database URI for MySQL
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@{server_ip}/{db_name}'

        # Attempt to connect to the database
        try:
            # Create an engine to verify the connection
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            #print("engine", engine)

            # Test connection by executing a basic query
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logging.debug(f"Connection successful: {result.fetchone()}")

                # Fetch and show tables
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]
                logging.debug(f"Tables found: {tables}")
                if not tables:
                    message = "The database is empty. No tables found."
                else:
                    message = "Existing tables: " + ", ".join(tables)

            return jsonify(message=message), 200

        except OperationalError as e:
            logging.error(f"Connection failed: {str(e)}")
            return jsonify(message=f"Connection failed: {str(e)}"), 500
        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return jsonify(message=f"An unexpected error occurred: {str(e)}"), 500

    # Get tables and their content
    @app.route('/get_tables', methods=['GET'])
    def get_tables():
        try:
            # Create an engine to verify the connection
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])           

            # Test connection by executing a basic query
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logging.debug(f"Connection successful: {result.fetchone()}")

                # Fetch the list of tables
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]

                if not tables:
                    return jsonify(message="No tables found."), 200

                # Step 2: Fetch the content of each table
                tables_data = {}
                for table in tables:
                    table_result = connection.execute(text(f"SELECT * FROM `{table}`"))                    

                    # Properly converting each row to a dictionary
                    rows = [dict(row._mapping) for row in table_result]  # Using _mapping to access data in row

                    tables_data[table] = rows                    

                return jsonify(tables=tables, data=tables_data), 200

        except Exception as e:
            return jsonify(message=f"Error fetching tables and data: {str(e)}"), 500


    """
    # Get tables and their content
    @app.route('/get_tables', methods=['GET'])
    def get_tables():
        try:
            # Create an engine to verify the connection
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

            # Test connection by executing a basic query
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logging.debug(f"Connection successful: {result.fetchone()}")

                # Fetch the list of tables
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]

                if not tables:
                    return jsonify(message="No tables found."), 200

                # Set the default user as root
                user = 'root'

                # Check if there are more than 2 tables
                if len(tables) > 2:
                    # Get a random table from the list of tables
                    random_table = random.choice(tables)
                    # Set the permission to deny for the random table
                    try:
                        connection.execute(f"GRANT SELECT ON `{random_table}` TO '{user}' WITH GRANT OPTION;")
                    except Exception as e:
                        # Trigger the default error for permission denied
                        return jsonify(message=f"Permission denied : {str(e)}"), 403

                # Return the list of tables and their data
                tables_data = {}
                for table in tables:
                    table_result = connection.execute(text(f"SELECT * FROM `{table}`"))

                    rows = [dict(row._mapping) for row in table_result]
                    tables_data[table] = rows

                return jsonify(tables=tables, data=tables_data), 200

        except Exception as e:
            return jsonify(message=f"Error fetching tables and data: {str(e)}"), 500
        """
        # Get tables and their content
    """
    @app.route('/get_tables', methods=['GET'])
    def get_tables():
        try:
            # Create an engine to verify the connection
            engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

            # Test connection
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logging.debug(f"Connection successful: {result.fetchone()}")

                # Fetch the list of tables
                result = connection.execute(text("SHOW TABLES;"))
                tables = [row[0] for row in result]

                if not tables:
                    return jsonify(message="No tables found."), 200

                accessible_tables_data = {}
                user = app.config.get('username')  # Ensure you capture the connected user

                for table in tables:
                    try:
                        # Check if the user has access to the table
                        permission_check = connection.execute(text(f"SHOW GRANTS FOR '{user}'")).fetchall()
                        
                        # Check for SELECT permission on the specific table
                        has_access = any(f"SELECT ON `{table}`" in str(grant) for grant in permission_check)

                        if has_access:
                            # If user has access, fetch the data from the table
                            table_result = connection.execute(text(f"SELECT * FROM `{table}`"))
                            rows = [dict(row._mapping) for row in table_result]
                            accessible_tables_data[table] = rows
                        else:
                            logging.warning(f"{user} does not have access to {table}.")

                    except Exception as e:
                        logging.error(f"Error checking access for {table}: {str(e)}")

                return jsonify(data=accessible_tables_data), 200 if accessible_tables_data else 404

        except Exception as e:
            return jsonify(message=f"Error fetching tables and data: {str(e)}"), 500
        """


    return app

if __name__ == '__main__':
    app = create_app()  # Create app instance
    app.run(debug=True)