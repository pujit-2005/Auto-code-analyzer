import sqlite3
import os

password = "admin123"

def get_user(username):
    conn = sqlite3.connect("users.db")
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    result = conn.execute(query)
    return result.fetchall()

def delete_file(filename):
    os.system("rm " + filename)

name = input("Enter username: ")
print(get_user(name))