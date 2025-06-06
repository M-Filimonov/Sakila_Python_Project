from dbmaster import DbMaster
from typing import Tuple, Optional, Dict, List
import error_handler

def create_sql_query(where_condition: str, order_condition: str) -> str:
    """
    Create a full SQL query by inserting the given WHERE condition.

    Args:
        where_condition (str): The condition to be used in the WHERE clause.
        order_condition (str): The condition to be used in the ORDER BY clause.

    Returns:
        str: The full SQL query.
    """
    query = f'''
            SELECT  f.film_id as fid,
                    f.title as title,
                    f.release_year as year,
                    c.name as category,
                    f.description as description,
                    GROUP_CONCAT(CONCAT(a.last_name, ' ', a.first_name) SEPARATOR ', ') as actors,
                    f.rental_rate as price,
                    f.length as length,
                    f.rating as rating,
                    CASE rating
                        WHEN 'G' THEN 'General Audiences - All ages admitted'
                        WHEN 'PG' THEN 'Parental Guidance Suggested - Some material may not be suitable for children'
                        WHEN 'PG-13' THEN 'Parents Strongly Cautioned - Some material may be inappropriate for children under 13'
                        WHEN 'R' THEN 'Restricted - Under 17 requires accompanying parent or adult guardian'
                        WHEN 'NC-17' THEN 'Adults Only - No one 17 and under admitted'
                        ELSE 'Not Rated'
                    END as rating_description                                                        
           FROM category c
                LEFT JOIN film_category fc ON c.category_id = fc.category_id
                LEFT JOIN film f ON fc.film_id = f.film_id
                JOIN film_actor fa ON f.film_id = fa.film_id
                JOIN actor a ON fa.actor_id = a.actor_id 
            WHERE {where_condition}
            GROUP BY f.film_id, f.title, f.release_year, c.name, f.description, f.rental_rate, f.length, f.rating
            ORDER BY  {order_condition};
            '''
    return query


def get_info_from_db(db: DbMaster, menu: str, params: Optional[Tuple] = None) -> List[Dict]:
    """
    Retrieves information from the database based on the given 'menu' and 'params'.

    Args:
        db (DbMaster): Database connection object.
        menu (str): Query type (e.g., "category_list", "year_list").
        params (Optional[Tuple]): Parameters for the SQL query (default is None).

    Returns:
        List[Dict]: Results of the SQL query as a list of dictionaries.

    Raises:
        ValueError: If the query parameters are invalid.
        RuntimeError: If an error occurs during SQL query execution.
    """
    # Validate the parameters
    if params and not isinstance(params, tuple):
        raise ValueError("Params should be a tuple or None.")

    if not menu:
        error_handler.handle_non_blocking_error("Invalid Input", "Menu cannot be empty or None.")
        return []

    query = None

    # Using match-case to handle different queries
    match menu:
        # Categories (no parameters)
        case "category_list":
            query = '''
                SELECT  category_id as Nr,
                        name as category
                FROM category 
                ORDER BY category_id;
                '''

        # Movie years for a category (expects parameters: (category,))
        case "year_list":
            query = '''
                SELECT DISTINCT f.release_year as year
                FROM film f 
                    JOIN film_category fc ON f.film_id = fc.film_id
                    JOIN category c ON fc.category_id = c.category_id
                WHERE c.name = %s
                ORDER BY year;
                '''

        # List of actors (no parameters)
        case "actor_list":
            query = '''
                SELECT  actor_id as FID,
                last_name as LastName,
                first_name as FirstName
                FROM actor 
                ORDER BY last_name;
                '''

        # Movies by category and year (expects parameters: (category, year))
        case "film_by_category_and_year":
            query = create_sql_query("c.name = %s and f.release_year = %s","category, year")

        # Movies by actor (expects parameters: (actor,))
        case "film_by_actor":  # params: (actor,)
            query = create_sql_query("fa.actor_id = %s","year, title")

        # Movies by keyword in title and description (expects parameters: (keyword,keyword))
        case "film_by_keyword_both":
            query = create_sql_query("f.title LIKE %s or f.description LIKE %s", "year, title")

        # Movies by keyword in title (expects parameters: (keyword,))
        case "film_by_keyword_in_film_title":
            query = create_sql_query("f.title LIKE %s", "year, title")

        # Movies by keyword in description (expects parameters: (keyword,))
        case "film_by_keyword_in_film_description":
            query = create_sql_query("f.description LIKE %s", "year, title")

        # Showed popular queries from sakila.popular_query - no parameters
        case "show_popular_queries":
            query = '''
            SELECT  type_query as 'Query type',
                    text_query as 'Query text',
                    count as 'Frequency'
            FROM    sakila.popular_query
            ORDER BY count DESC;
            '''
        case _:
            error_handler.handle_non_blocking_error("Invalid Query", f"Menu '{menu}' is not recognized.")
            return []

    # Executing the query and handling exceptions
    try:
        if query and isinstance(query, str):
            res = db.execute_query(query, params or ())
            return res
    except RuntimeError as e:
        error_handler.handle_error("Runtime Error", str(e))
    except ValueError as e:
        error_handler.handle_error("Value Error", str(e))
    except Exception as e:
        error_handler.handle_error("Unexpected Error", str(e))

    return []
