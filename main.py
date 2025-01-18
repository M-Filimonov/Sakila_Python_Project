import os
import tkinter as tk
from typing import Optional, Dict
from dotenv import load_dotenv
from dbmaster import DbMaster
import utils

# Load environment variables
load_dotenv()
DB_SETTINGS: Dict[str, Optional[str]] = {
    "host": os.getenv('DB_HOST'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DB_NAME'),
}

# Constants
MWINDOW_WIDTH: int = 420
MWINDOW_HEIGHT: int = 300
ICON_PATHS: Dict[str, str] = {
    "keyword": 'icons/menu_keyword.png',
    "category": 'icons/menu_category.png',
    "actor": 'icons/menu_actor.png',
    "popular": 'icons/menu_popular.png',
    "exit": 'icons/menu_exit.png',
}


def initialize_database_connection() -> Optional[DbMaster]:
    """
    Create and return the database connection.

    Returns:
        DbMaster: The database connection object or None if connection failed.
    """
    try:
        return DbMaster(**DB_SETTINGS)  # type: ignore
    except RuntimeError as error:
        print(f"Database connection error: {error}")
        return None


def setup_main_window() -> tk.Tk:
    """
    Initialize and configure the main Tkinter window.

    Returns:
        tk.Tk: The main Tkinter window object.
    """
    root: tk.Tk = tk.Tk()
    root.title('SAKILA Database Search: MAKE YOUR CHOICE:')
    root.resizable(False, False)
    screen_width: int = root.winfo_screenwidth()
    screen_height: int = root.winfo_screenheight()
    position_x: int = (screen_width // 2) - (MWINDOW_WIDTH // 2)
    position_y: int = (screen_height // 2) - (MWINDOW_HEIGHT // 2)
    root.geometry(f'{MWINDOW_WIDTH}x{MWINDOW_HEIGHT}+{position_x}+{position_y}')

    # Ensure the window is active and gets the focus
    root.lift()  # Bring the window to the front
    root.focus_force()  # Force focus on the window
    return root


def create_buttons(frame: tk.Frame, database_connection: DbMaster, root: tk.Tk) -> None:
    """
    Create and configure buttons with icons and their functionality.

    Args:
        frame (tk.Frame): The parent frame where buttons will be placed.
        database_connection (DbMaster): The database connection object.
        root (tk.Tk): The main Tkinter window object.
    """
    # Save icons as an attribute of the root to keep references
    root.icons = {key: tk.PhotoImage(file=path) for key, path in ICON_PATHS.items()}

    # Configure grid layout in the parent frame
    frame.grid_rowconfigure(0, weight=1)  # Row growable - weight=1 makes the row and column "stretchy"
    frame.grid_columnconfigure(0, weight=1)  # Column growable

    buttons = [
        ("  1. Search by KEYWORD", root.icons["keyword"], lambda: utils.search_by_keyword(database_connection, root)),
        ("  2. Search by film CATEGORY & YEAR", root.icons["category"], lambda: utils.search_by_category_and_year(database_connection, root)),
        ("  3. Search by ACTOR", root.icons["actor"], lambda: utils.search_by_actor(database_connection, root)),
        ("  4. Show POPULAR QUERIES", root.icons["popular"], lambda: utils.show_popular_queries(database_connection)),
        ("  5. EXIT", root.icons["exit"], lambda: utils.exit_program(database_connection, root)),
    ]

    for idx, (text, icon, command) in enumerate(buttons):
        # Create button and use 'sticky' to center them
        tk.Button(
            frame,
            text=text,
            image=icon,
            compound='left', #alignment relative to icon
            anchor='w', # alignment left
            width=250, # button width
            bg='#add8e6', # background color (LightBlue)
            command=command # action on click
        ).grid(
            row=idx,
            column=0,
            sticky='nsew', # stretches to fill the entire available cell (horizontally and vertically)
            pady=5 # adds vertical padding (top and bottom)
        )


    # Add padding to center content better vertically
    frame.grid_rowconfigure(len(buttons), weight=1)


def main() -> None:
    """
    Main entry point for the application.
    Initializes database connection, sets up the main window,
    creates buttons, and starts the Tkinter main loop.
    """
    # Initialize database connection
    database_connection: Optional[DbMaster] = initialize_database_connection()
    if database_connection is None:
        print("Database connection failed. Exiting program.")
        return

    # Setup Tkinter root window
    root: tk.Tk = setup_main_window()

    # Create main frame (with centered buttons)
    frame: tk.Frame = tk.Frame(root, padx=20, pady=20)
    frame.pack(expand=True, fill='both')  # Center the content

    # Create buttons
    create_buttons(frame, database_connection, root)

    # Bind keys to actions
    root.bind('1', lambda event: utils.search_by_keyword(database_connection, root))
    root.bind('2', lambda event: utils.search_by_category_and_year(database_connection))
    root.bind('3', lambda event: utils.search_by_actor(database_connection))
    root.bind('4', lambda event: utils.show_popular_queries(database_connection))
    root.bind('5', lambda event: utils.exit_program(database_connection, root))

    # Run the Tkinter main loop
    root.mainloop()


if __name__ == '__main__':
    main()
