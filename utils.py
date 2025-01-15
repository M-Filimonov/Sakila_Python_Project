from gui import display_table, get_keyword
from query import get_info_from_db
from tkinter import messagebox

def search_by_keyword(db,root):
    try:
        res = get_keyword(root,"Keyword to search")
        keyword = res.get('keyword')
        if res.get('both'):
            results = get_info_from_db(db, "film_by_keyword_both", (f"%{keyword}%", f"%{keyword}%"))
        elif res.get('title'):
            results = get_info_from_db(db, "film_by_keyword_in_film_title", (f"%{keyword}%",))
        elif res.get('description'):
            results = get_info_from_db(db, "film_by_keyword_in_film_description", (f"%{keyword}%",))
        else:
            results = []

        if results:
            display_table(results, f"Films by keyword '{keyword}'  to EXIT: (<Double-Click> or <Enter>)")
            db.insert_query_log('film_by_keyword', f'{keyword}') # write in popular_query
        else:
            messagebox.showerror("Warning!", f"No films found matching the keyword: {keyword}!")
    except Exception as e:
        messagebox.showerror("Error!", f"Error occurred: {e}")


def search_by_category_and_year(db):
    try:
        cat = get_info_from_db(db, "category_list") # category list from db
        res = display_table(cat, 'Choice a category:')
        category = res.get('category')
        yr = get_info_from_db(db, "year_list", (category,))  # related category year list from db
        res = display_table(yr, 'Choice a year:')
        year = res.get('year')
        if category and year:
            results = get_info_from_db(db, "film_by_category_and_year", (category, year))
            display_table(results, f"Films by category '{category}' and year '{year}' to EXIT: (<Double-Click> or <Enter>)")
            db.insert_query_log('film_by_category_and_year',f'{category},{year}') # write in popular_query
    except Exception as e:
        messagebox.showerror("Error!", f"Error occurred: {e}")


def search_by_actor(db):
    try:
        act = get_info_from_db(db, "actor_list") # actors list from db
        res = display_table(act, 'Choice an Actor:') # output in Window
        actor_id = res.get('Nr')
        if actor_id:
            results = get_info_from_db(db, "film_by_actor", (actor_id,))
            display_table(results, f"Films by Actor '{res.get('name')}' to EXIT: (<Double-Click> or <Enter>)")
            db.insert_query_log('film_by_actor', f'{res.get('name')}') # write in popular_query
    except Exception as e:
        messagebox.showerror("Error!", f"Error occurred: {e}")


def show_popular_queries(db):
    try:
        pq = get_info_from_db(db, "show_popular_queries")  # popular_queries list from db
        display_table(pq, 'Popular queries to Database:')  # output in Window
    except Exception as e:
        messagebox.showerror("Error!", f"Error occurred: {e}")

def exit_program(db, root):
    if db is not None:
        db.close()
    root.quit()
