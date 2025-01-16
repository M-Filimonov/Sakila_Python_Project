import os
import tkinter as tk
from typing import Optional, Dict
from dotenv import load_dotenv
from dbmaster import DbMaster
from utils import search_by_keyword, search_by_category_and_year, search_by_actor, show_popular_queries, exit_program

# Load environment variables
load_dotenv()
DB_SETTINGS: Dict[str, Optional[str]] = {
    "host": os.getenv('DB_HOST'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASSWORD'),
    "database": os.getenv('DB_NAME'),
}

# Constants
MWINDOW_WIDTH: int = 450
MWINDOW_HEIGHT: int = 300
ICON_PATHS: Dict[str, str] = {
    "keyword": 'icons/menu_keyword.png',
    "category": 'icons/menu_category.png',
    "actor": 'icons/menu_actor.png',
    "popular": 'icons/menu_popular.png',
    "exit": 'icons/menu_exit.png',
}


def initialize_database_connection() -> Optional[DbMaster]:
    """Create and return the database connection."""
    try:
        return DbMaster(**DB_SETTINGS)  # type: ignore
    except RuntimeError as error:
        print(f"Database connection error: {error}")
        return None


def setup_main_window() -> tk.Tk:
    """Initialize and configure the main Tkinter window."""
    root: tk.Tk = tk.Tk()
    root.title('SAKILA Database Search: MAKE YOUR CHOICE:')
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
    """Create and configure buttons with icons and their functionality."""
    # Save icons as an attribute of the root to keep references
    root.icons = {key: tk.PhotoImage(file=path) for key, path in ICON_PATHS.items()}

    # Configure grid layout in the parent frame
    frame.grid_rowconfigure(0, weight=1)  # Row growable - weight=1 makes the row and column "stretchy"
    frame.grid_columnconfigure(0, weight=1)  # Column growable

    buttons = [
        ("  1. Search by KEYWORD", root.icons["keyword"], lambda: search_by_keyword(database_connection, root)),
        ("  2. Search by film CATEGORY & YEAR", root.icons["category"], lambda: search_by_category_and_year(database_connection)),
        ("  3. Search by ACTOR", root.icons["actor"], lambda: search_by_actor(database_connection)),
        ("  4. Show POPULAR QUERIES", root.icons["popular"], lambda: show_popular_queries(database_connection)),
        ("  5. EXIT", root.icons["exit"], lambda: exit_program(database_connection, root)),
    ]

    for idx, (text, icon, command) in enumerate(buttons):
        # Create button and use 'sticky' to center them
        tk.Button(
            frame, text=text, image=icon, compound='left',
            anchor='w', width=300, command=command
        ).grid(row=idx, column=0, sticky='nsew', pady=5)

    # Add padding to center content better vertically
    frame.grid_rowconfigure(len(buttons), weight=1)



def main() -> None:
    """Main entry point for the application."""
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
    root.bind('1', lambda event: search_by_keyword(database_connection, root))
    root.bind('2', lambda event: search_by_category_and_year(database_connection))
    root.bind('3', lambda event: search_by_actor(database_connection))
    root.bind('4', lambda event: show_popular_queries(database_connection))
    root.bind('5', lambda event: exit_program(database_connection, root))

    # Run the Tkinter main loop
    root.mainloop()



if __name__ == '__main__':
    main()
