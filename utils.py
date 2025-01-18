import gui
import query
from tkinter import messagebox
import error_handler

def search_by_keyword(db, root):
    try:
        keyword_and_search_rules_dict = gui.get_keyword(root, "Keyword to search")
        if keyword_and_search_rules_dict:
            keyword = keyword_and_search_rules_dict.get('keyword')
            if keyword_and_search_rules_dict.get('both'):
                answer = query.get_info_from_db(db, "film_by_keyword_both", (f"%{keyword}%", f"%{keyword}%"))
            elif keyword_and_search_rules_dict.get('title'):
                answer = query.get_info_from_db(db, "film_by_keyword_in_film_title", (f"%{keyword}%",))
            elif keyword_and_search_rules_dict.get('description'):
                answer = query.get_info_from_db(db, "film_by_keyword_in_film_description", (f"%{keyword}%",))
            else:
                answer = []
            if answer:
                movie = gui.display_table(answer, f"Films by keyword '{keyword}' | >> more Info: <Double-Click> or <Enter>")
                gui.display_record(root,movie)
                db.insert_query_log('film_by_keyword', f'{keyword}')
            else:
                messagebox.showerror("Warning!", f"No Movie found matching the keyword: < {keyword} > !")

    except Exception as e:
        error_handler.handle_error_with_recommendation("Unexpected Error", str(e))

def search_by_category_and_year(db, root):
    try:
        category_list = query.get_info_from_db(db, "category_list")
        if category_list:
            selected_category = gui.display_table(category_list, 'Choice a category:')
            if selected_category:
                category = selected_category.get('category')
                year_list = query.get_info_from_db(db, "year_list", (category,))
                if year_list:
                    selected_year = gui.display_table(year_list, 'Choice a year:')
                    if selected_year:
                       year = selected_year.get('year')
                       if category and year:
                            results = query.get_info_from_db(db, "film_by_category_and_year", (category, year))
                            if results:
                                movie = gui.display_table(results, f"Films by category '{category}' and year '{year}' | >> more Info: <Double-Click> or <Enter>")
                                if movie:
                                    gui.display_record(root, movie)
                                    db.insert_query_log('film_by_category_and_year', f'{category},{year}')
    except Exception as e:
        error_handler.handle_error_with_recommendation("Unexpected Error", str(e))

def search_by_actor(db, root):
    try:
        actor_list = query.get_info_from_db(db, "actor_list")
        if actor_list:
           actor = gui.display_table(actor_list, 'Choice an Actor:')
           if actor:
                actor_id = actor.get('FID')
                results = query.get_info_from_db(db, "film_by_actor", (actor_id,))
                if results:
                    movie = gui.display_table(results, f"Films by Actor: {actor.get('FirstName')} {actor.get('LastName')} | >> more Info: <Double-Click> or <Enter>")
                    db.insert_query_log('film_by_actor', f'{actor.get('FirstName')} {actor.get('LastName')}')
                    gui.display_record(root, movie)
    except Exception as e:
        error_handler.handle_error_with_recommendation("Unexpected Error", str(e))

def show_popular_queries(db):
    try:
        popular_query_list = query.get_info_from_db(db, "show_popular_queries")
        if popular_query_list:
            gui.display_table(popular_query_list, "Popular queries to Database: | >> EXIT: <Double-Click> or <Enter>")
        else:
            messagebox.showerror("Warning!", f"Popular queries Database is empty!")
    except Exception as e:
        error_handler.handle_error_with_recommendation("Unexpected Error", str(e))

def exit_program(db, root):
    if db is not None:
        db.close()
    root.quit()
