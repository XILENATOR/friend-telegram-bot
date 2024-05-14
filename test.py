import sqlite3
connection = sqlite3.connect("friend_place_servers.db")
cursor = connection.cursor()
# with connection:
#     cursor.execute('INSERT INTO Users VALUES ("Ilya", "Sorokin", 14, "Edit Profile", 5217670122, "XILENATOR92", "5217670122")')
# with connection:
#     cursor.execute('UPDATE Users SET Name = "ilia" WHERE ID = 669548690')
a = cursor.execute("SELECT * FROM Users").fetchall()
print(a)