import pygame
import sqlite3



def create_database():
    
    connection = sqlite3.connect("highscore.db")
    cursor = connection.cursor()
    
   
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Highscore (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            score INTEGER
        )
    """)
    
   
    cursor.execute("SELECT COUNT(*) FROM Highscore")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO Highscore (score) VALUES (0)")
    
    
    connection.commit()
    connection.close()

def get_highscore():
    connection = sqlite3.connect("highscore.db")
    cursor = connection.cursor()
    
    cursor.execute("SELECT score FROM Highscore WHERE id = 1")
    highscore = cursor.fetchone()[0]
    
    connection.close()
    return highscore

def update_highscore(new_score):
    connection = sqlite3.connect("highscore.db")
    cursor = connection.cursor()
    
    current_highscore = get_highscore()
    if new_score > current_highscore:
        cursor.execute("UPDATE Highscore SET score = ? WHERE id = 1", (new_score,))
    
    connection.commit()
    connection.close()
