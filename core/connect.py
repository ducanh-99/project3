import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="ducanh",
  password="Ducanh@99"
)

print(mydb)