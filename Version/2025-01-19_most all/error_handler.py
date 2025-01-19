import logging
from tkinter import messagebox

# setting up logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levellevel_name)s - %(message)s')

def handle_error(error_type: str, error_message: str):
    """
    Handle and log an error by showing an error message box and logging the error.

    Args:
        error_type (str): The type of error.
        error_message (str): The detailed error message.
    """
    detailed_message = f"{error_type} occurred: {error_message}"
    messagebox.showerror("Error", detailed_message)
    logging.error(detailed_message)

def handle_non_blocking_error(error_type: str, error_message: str):
    """
    Handle and log a non-blocking error by showing an error message box with an option to continue.
    If the user chooses not to continue, raise a RuntimeError.

    Args:
        error_type (str): The type of error.
        error_message (str): The detailed error message.
    """
    detailed_message = f"{error_type} occurred: {error_message}\nDo you want to continue?"
    if messagebox.askyesno("Error", detailed_message):
        logging.warning(f"Non-blocking {detailed_message}")
    else:
        logging.error(f"Blocking {detailed_message}")
        raise RuntimeError(detailed_message)

def handle_error_with_recommendation(error_type: str, error_message: str):
    """
    Handle and log an error by showing an error message box with recommendations and logging the error.

    Args:
        error_type (str): The type of error.
        error_message (str): The detailed error message.
    """
    recommendations = {
        "Database Error": "Please check your database connection settings and try again.",
        "Unexpected Error": "Please restart the application and try again. If the problem persists, contact support."
    }
    detailed_message = f"{error_type} occurred: {error_message}\n\nRecommendation: {recommendations.get(error_type, 'Please try again later.')}"
    messagebox.showerror("Error", detailed_message)
    logging.error(detailed_message)
