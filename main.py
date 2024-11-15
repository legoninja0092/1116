import os
import json
import sqlite3
from typing import Any
import lib

DB_PATH = 'movies.db'
JSON_IN_PATH = 'movies.json'
JSON_OUT_PATH = 'exported.json'

def main() -> None:
    # 建立資料庫及資料表
    if not os.path.exists(DB_PATH):
        lib.connect_db(DB_PATH)
        lib.create_table(DB_PATH)

    while True:
        print("\n----- 電影管理系統 -----")
        print("1. 匯入電影資料檔")
        print("2. 查詢電影")
        print("3. 新增電影")
        print("4. 修改電影")
        print("5. 刪除電影")
        print("6. 匯出電影")
        print("7. 離開系統")
        print("------------------------")
        choice = input("請選擇操作選項 (1-7): ")

        if choice == '1':
            try:
                lib.import_movies(DB_PATH, JSON_IN_PATH)
                print("電影已匯入")
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"匯入資料發生錯誤: {e}")
        elif choice == '2':
            lib.search_movies(DB_PATH)
        elif choice == '3':
            lib.add_movie(DB_PATH)
        elif choice == '4':
            lib.modify_movie(DB_PATH)
        elif choice == '5':
            lib.delete_movies(DB_PATH)
        elif choice == '6':
            try:
                lib.export_movies(DB_PATH, JSON_OUT_PATH)
                print("電影資料已匯出至 exported.json")
            except Exception as e:
                print(f"匯出資料發生錯誤: {e}")
        elif choice == '7':
            print("系統已退出。")
            break
        else:
            print("請輸入正確的選項")

if __name__ == '__main__':
    main()
