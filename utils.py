import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict, List, Optional

import gui
import query
import error_handler
from dbmaster import DbMaster

def search_by_keyword(db: DbMaster, root: tk.Tk) -> None:
    """
    Search for films based on a keyword and display the results in a GUI table.

    The function first retrieves a keyword and related search options from the user via a dialog. Depending on
    the selected search options, it queries the database for films either by their title, description, or both.
    The results are displayed  in a table within a Tkinter GUI. Any selected movie can be further inspected in a
    detailed view. Additionally, successful queries are logged for future analysis. If no results are found,
    an error message is displayed to  the user.

    :param db: The database interface object that allows interaction with a database.
    :type db: DbMaster
    :param root: The root Tkinter window object used for displaying the dialog and results.
    :type root: tk.Tk
    :return: This function does not return any value
    :rtype: None

    """
    try:
        # Get keyword and search rules from the user
        keyword_and_search_rules_dict: Optional[Dict[str, Any]] = gui.get_keyword(root, "Keyword to search")
        if keyword_and_search_rules_dict:
            # Extract the keyword
            keyword = keyword_and_search_rules_dict.get('keyword')
            if not keyword:
                display_error("No keyword selected! Try again")
                return

            # Determine the search scope based on the provided options
            if keyword_and_search_rules_dict.get('both'):
                answer = query.get_info_from_db(
                    db, "film_by_keyword_both", (f"%{keyword}%", f"%{keyword}%")
                )
            elif keyword_and_search_rules_dict.get('title'):
                answer = query.get_info_from_db(
                    db, "film_by_keyword_in_film_title", (f"%{keyword}%",)
                )
            elif keyword_and_search_rules_dict.get('description'):
                answer = query.get_info_from_db(
                    db, "film_by_keyword_in_film_description", (f"%{keyword}%",)
                )
            else:
                answer = []

            # Handle the search results
            if answer:
                movie = gui.display_table(
                    answer, f"Films by keyword '{keyword}' | >> more Info: <Double-Click> or <Enter>"
                )
                if movie:
                    gui.display_record(root, movie)
                    # Log the query in the "popular_query" database
                    db.insert_query_log('film_by_keyword', f'{keyword}')
            else:
                display_error(f"No Movie found matching the keyword: < {keyword} > !")

    except Exception as e:
        error_handler.handle_error_with_recommendation("An unexpected error occurred:", str(e))


def search_by_category_and_year(db: DbMaster, root: tk.Tk) -> None:
    """
    Search for movies by category and year using GUI-based selection and database querying.

    This function allows users to interactively select a category and year from the available
    choices fetched from the database. Upon successful selection, it searches for and displays
    movies that match the selected category and year. If no results are found at any stage of
    the process, the user is notified with an appropriate error message. Results can also be
    reviewed in detail, and the performed query is logged accordingly.

    :param db: Instance of DbMaster for database interactions.
    :type db: DbMaster
    :param root: Instance of tkinter root object used for GUI rendering.
    :type root: tk.Tk
    :return: This function does not return a value.
    :rtype: None
    """
    try:
        def select_category():
            categories = query.get_info_from_db(db, "category_list")
            if not categories:
                display_error("No categories found!")
                return None
            selected = gui.display_table(categories, 'Choose a category:')
            return selected.get('category') if selected else None


        def select_year(category):
            years = query.get_info_from_db(db, "year_list", (category,))
            if not years:
                display_error(f"No years found for category: {category}")
                return None
            selected = gui.display_table(years, 'Choose a year:')
            return selected.get('year') if selected else None

        # Choose category
        category = select_category()
        if not category:
           display_error("No category selected! Try again")
           return

        # Choose year
        year = select_year(category)
        if not year:
            display_error("No year selected! Try again")
            return

        # Search for movies
        results = query.get_info_from_db(db, "film_by_category_and_year", (category, year))
        if not results:
            display_error(f"No movies found for category: {category} and year: {year}")
            return

        movie = gui.display_table(
            results,
            f"Films by category '{category}' and year '{year}' | >> more Info: <Double-Click> or <Enter>"
        )
        if movie:
            gui.display_record(root, movie)
            # Insert actor search information into the "popular_query" database
            db.insert_query_log('film_by_category_and_year', f'{category},{year}')
    except Exception as e:
        error_handler.handle_error_with_recommendation("Unexpected Error", str(e))


def search_by_actor(db: DbMaster, root: tk.Tk) -> None:
    """
    Searches and displays films associated with a selected actor from the database.

    The function provides an interface for the user to select an actor from
    a list, retrieves the corresponding films related to the selected actor,
    and displays the detailed information of a selected film. If no data is
    found or an error occurs during the selection process, appropriate error
    messages will be displayed.

    :param db: Database interaction object for executing queries and logging.
    :type db: DbMaster
    :param root: Tkinter root window used as the parent UI container.
    :type root: tk.Tk
    :return: This function does not return a value.
    :rtype: None
    """

    def get_actor(actor_list: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Displays a list of actors and returns the selected actor.

        Args:
            actor_list (List[Dict[str, Any]]): List of actors retrieved from the database.

        Returns:
            Optional[Dict[str, Any]]: Dictionary representing the selected actor,
            or None if no selection was made.
        """
        return gui.display_table(actor_list, 'Choose an Actor:')

    def get_films_by_actor(actor: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Retrieves a list of films associated with the selected actor.

        Args:
            actor (Dict[str, Any]): Dictionary containing information about the selected actor.

        Returns:
            List[Dict[str, Any]]: List of films associated with the actor.
        """
        actor_id = actor.get('FID')
        return query.get_info_from_db(db, "film_by_actor", (actor_id,))

    # Retrieve the list of actors
    actor_list = query.get_info_from_db(db, "actor_list")
    if not actor_list:
        display_error("No actors found in the database!")
        return

    # Allow the user to select an actor
    actor = get_actor(actor_list)
    if not actor:
        display_error("No actor selected! Try again.")
        return

    # Retrieve the list of films by the selected actor
    films = get_films_by_actor(actor)
    if not films:
        display_error(f"No movies found for the actor: {actor.get('FirstName')} {actor.get('LastName')}!")
        return

    # Allow the user to select a film from the list
    selected_film = gui.display_table(
        films,
        f"Films by Actor: {actor.get('FirstName')} {actor.get('LastName')} | >> more Info: <Double-Click> or <Enter>"
    )
    if not selected_film:
        display_error("No movie selected!")
        return

    # Display detailed information about the selected film
    gui.display_record(root, selected_film)
    # Insert actor search information into the "popular_query" database
    db.insert_query_log('film_by_actor', f"{actor.get('FirstName')} {actor.get('LastName')}")

def show_popular_queries(db: DbMaster) -> None:
    """
    Displays popular queries from the database in a table format. If the database table
    "popular_query" does not exist or contains no entries, an error message is displayed.

    This function fetches the information from the database table named
    "popular_query" using the provided database connection and displays
    it in a user interface table. In case of any unexpected error during execution,
    a generic error handler is invoked with the appropriate error message.

    :param db: The database connection object of type `DbMaster` used
        to interact with the database.
    :type db: DbMaster

    :return: This function does not return a value.
    :rtype: None
    """

    try:
        # Check if table "popular_query" exists
        if not db.check_db_table("popular_query"):
            display_error("There are no entries in the 'Popular Queries' database yet!")
            return

        # Get popular queries from the database
        popular_query_list = query.get_info_from_db(db, "show_popular_queries")
        if popular_query_list:
            gui.display_table(popular_query_list, "Popular queries to Database: | >> EXIT: <Double-Click> or <Enter>")
        else:
             raise ValueError("There are no entries in the 'Popular Queries' database yet!")
    except RuntimeError as e:
        error_handler.handle_error("Runtime Error", str(e))
    except ValueError as e:
        display_error("There are no entries in the 'Popular Queries' database yet!")



def exit_program(db: DbMaster, root: tk.Tk) -> None:
    """
    Closes the database connection (if it exists) and exits the Tkinter application.

    Args:
        db (DbMaster): Database connection object, or None if no connection exists.
        root (tk.Tk): Tkinter root window object.
    """
    if db is not None:
        db.close()
    root.quit()

def display_error(message: str) -> None:
    """
    Displays an error message in a messagebox.

    Args:
        message (str): The error message to be displayed.
    """
    messagebox.showerror("Warning!", message)