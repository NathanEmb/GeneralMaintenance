# Module Imports
import mariadb
import sys

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="Nathan",
        password="password",
        host="192.168.0.112",
        port=3306,
        database="GeneralMaintenance"

    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

# Get Cursor
cur = conn.cursor()

cur.execute("SELECT `User`,`Message` FROM `SmashBrosMessageLog` WHERE `User`='Chasin'")

for (User, Message) in cur:
    print(f"User: {User}, Message: {Message}")