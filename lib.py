import sqlite3
import json
from typing import Any

DB_PATH = 'movies.db'


def connect_db(db_path: str) -> sqlite3.Connection:
    """
    連接資料庫，並回傳連接對象
    :param db_path: 資料庫的路徑
    :return: SQLite Connection 對象
    """
    try:
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.DatabaseError as e:
        print(f"資料庫連接失敗: {e}")
        raise


def create_table(db_path: str) -> None:
    """
    建立 movies 資料表
    :param db_path: 資料庫的路徑
    """
    try:
        with connect_db(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    director TEXT NOT NULL,
                    genre TEXT NOT NULL,
                    year INTEGER NOT NULL,
                    rating REAL CHECK(rating >= 1.0 AND rating <= 10.0)
                )
            ''')
            conn.commit()
    except sqlite3.DatabaseError as e:
        print(f"資料表建立失敗: {e}")
    except Exception as e:
        print(f'發生其它錯誤: {e}')


def import_movies(db_path: str, json_path: str) -> None:
    """
    匯入 movies.json 資料至資料表
    :param db_path: 資料庫的路徑
    :param json_path: JSON 資料檔的路徑
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            movies = json.load(file)
            with connect_db(db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany('''
                    INSERT INTO movies (title, director, genre, year, rating)
                    VALUES (:title, :director, :genre, :year, :rating)
                ''', movies)
                conn.commit()
    except FileNotFoundError:
        print('找不到電影資料檔')
    except json.JSONDecodeError:
        print('無法解析電影資料檔')
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")
    except Exception as e:
        print(f'發生其它錯誤: {e}')


def search_movies(db_path: str) -> None:
    """
    查詢全部或指定電影
    :param db_path: 資料庫的路徑
    """
    try:
        with connect_db(db_path) as conn:
            cursor = conn.cursor()
            search_all = input("查詢全部電影嗎？(y/n): ").strip().lower()
            if search_all == 'y':
                cursor.execute("SELECT * FROM movies")
            else:
                movie_title = input("請輸入電影名稱: ")
                cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))

            rows = cursor.fetchall()
            if rows:
                print("\n電影名稱\t\t導演\t\t\t類型\t\t上映年份\t評分")
                print("-" * 72)
                for row in rows:
                    print(f"{row['title']:{chr(12288)}<10}\t{row['director']:{chr(12288)}<10}\t{row['genre']}\t{row['year']}\t{row['rating']}")
            else:
                print("查無資料")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")
    except Exception as e:
        print(f'發生其它錯誤: {e}')


def add_movie(db_path: str) -> None:
    """
    新增一部電影到資料表
    :param db_path: 資料庫的路徑
    """
    try:
        title = input("電影名稱: ")
        director = input("導演: ")
        genre = input("類型: ")
        year = int(input("上映年份: "))
        rating = float(input("評分 (1.0 - 10.0): "))

        with connect_db(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO movies (title, director, genre, year, rating)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, director, genre, year, rating))
            conn.commit()
            print("電影已新增")
    except ValueError:
        print("年份或評分格式不正確")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")
    except Exception as e:
        print(f'發生其它錯誤: {e}')


def modify_movie(db_path: str) -> None:
    """
    修改資料表中的電影資料
    :param db_path: 資料庫的路徑
    """
    try:
        movie_title = input("請輸入要修改的電影名稱: ")
        with connect_db(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))
            row = cursor.fetchone()

            if row:
                print("\n電影名稱\t\t導演\t\t\t類型\t\t上映年份\t評分")
                print("-" * 72)
                print(f"{row['title']:{chr(12288)}<10}\t{row['director']:{chr(12288)}<10}\t{row['genre']}\t{row['year']}\t{row['rating']}")

                new_title = input("請輸入新的電影名稱 (若不修改請直接按 Enter): ") or row['title']
                new_director = input("請輸入新的導演 (若不修改請直接按 Enter): ") or row['director']
                new_genre = input("請輸入新的類型 (若不修改請直接按 Enter): ") or row['genre']
                new_year = input("請輸入新的上映年份 (若不修改請直接按 Enter): ") or row['year']
                new_rating = input("請輸入新的評分 (1.0 - 10.0) (若不修改請直接按 Enter): ") or row['rating']

                cursor.execute('''
                    UPDATE movies
                    SET title = ?, director = ?, genre = ?, year = ?, rating = ?
                    WHERE id = ?
                ''', (new_title, new_director, new_genre, new_year, new_rating, row['id']))
                conn.commit()
                print("資料已修改")
            else:
                print("查無符合的電影資料")
    except ValueError:
        print("年份或評分格式不正確")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")
    except Exception as e:
        print(f'發生其它錯誤: {e}')


def delete_movies(db_path: str) -> None:
    """
    刪除資料表中的電影
    :param db_path: 資料庫的路徑
    """
    try:
        delete_all = input("刪除全部電影嗎？(y/n): ").strip().lower()
        with connect_db(db_path) as conn:
            cursor = conn.cursor()
            if delete_all == 'y':
                cursor.execute("DELETE FROM movies")
            else:
                movie_title = input("請輸入要刪除的電影名稱: ")
                cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))
                row = cursor.fetchone()

                if row:
                    print("\n電影名稱\t\t導演\t\t\t類型\t\t上映年份\t評分")
                    print("-" * 72)
                    print(f"{row['title']:{chr(12288)}<10}\t{row['director']:{chr(12288)}<10}\t{row['genre']}\t{row['year']}\t{row['rating']}")
                    confirm = input("是否要刪除(y/n): ").strip().lower()
                    if confirm == 'y':
                        cursor.execute("DELETE FROM movies WHERE id = ?", (row['id'],))
                        conn.commit()
                        print("電影已刪除")
                    else:
                        print("取消刪除")
                else:
                    print("查無符合的電影資料")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")
    except Exception as e:
        print(f'發生其它錯誤: {e}')


def export_movies(db_path: str, json_path: str) -> None:
    """
    匯出資料表中的電影至 JSON 檔案
    :param db_path: 資料庫的路徑
    :param json_path: 匯出的 JSON 資料檔路徑
    """
    try:
        with connect_db(db_path) as conn:
            cursor = conn.cursor()
            export_all = input("匯出全部電影嗎？(y/n): ").strip().lower()
            if export_all == 'y':
                cursor.execute("SELECT * FROM movies")
            else:
                movie_title = input("請輸入要匯出的電影名稱: ")
                cursor.execute("SELECT * FROM movies WHERE title LIKE ?", (f'%{movie_title}%',))

            rows = cursor.fetchall()
            if rows:
                with open(json_path, 'w', encoding='utf-8') as file:
                    json.dump([dict(row) for row in rows], file, ensure_ascii=False, indent=4)
            else:
                print("查無符合的電影資料")
    except sqlite3.DatabaseError as e:
        print(f"資料庫操作發生錯誤: {e}")
    except Exception as e:
        print(f'發生其它錯誤: {e}')
