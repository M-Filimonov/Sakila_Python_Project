import logging
from tkinter import messagebox

# setting up logging
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def handle_error(error_type: str, error_message: str):
    detailed_message = f"{error_type} occurred: {error_message}"
    messagebox.showerror("Error", detailed_message)
    logging.error(detailed_message)

def handle_non_blocking_error(error_type: str, error_message: str):
    detailed_message = f"{error_type} occurred: {error_message}\nDo you want to continue?"
    if messagebox.askyesno("Error", detailed_message):
        logging.warning(f"Non-blocking {detailed_message}")
    else:
        logging.error(f"Blocking {detailed_message}")
        raise RuntimeError(detailed_message)

def handle_error_with_recommendation(error_type: str, error_message: str):
    recommendations = {
        "Database Error": "Please check your database connection settings and try again.",
        "Unexpected Error": "Please restart the application and try again. If the problem persists, contact support."
    }
    detailed_message = f"{error_type} occurred: {error_message}\n\nRecommendation: {recommendations.get(error_type, 'Please try again later.')}"
    messagebox.showerror("Error", detailed_message)
    logging.error(detailed_message)
