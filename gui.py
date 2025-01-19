import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import List, Dict, Any

#======================================== display_table ============================================================
PIXEL_SCALE = 8
DEFAULT_WINDOW_WIDTH_PADDING = 500
DEFAULT_WINDOW_HEIGHT_PADDING = 150
DEFAULT_WINDOW_WIDTH = 400
DEFAULT_WINDOW_HEIGHT = 400
TABLE_ROW_HEIGHT = 100  # Default row height for calculation


def display_table(data: List[Dict[str, Any]], window_title: str) -> Dict[str, Any]:
    """
    Display a table using tkinter Treeview.

    Args:
        data (List[Dict[str, Any]]): The data to be displayed in the table.
        window_title (str): The title of the table window.

    Returns:
        Dict[str, Any]: The selected row from the table.
    """

    def initialize_tkinter_root_window() -> tk.Tk:
        """
        Ensure a tkinter root window exists and return it.

        Returns:
            tk.Tk: The root tkinter window.
        """
        if not tk._default_root:
            local_root = tk.Tk()
            local_root.withdraw()
        else:
            local_root = tk._default_root
        return local_root

    def create_table_window(ct_root: tk.Tk, title: str) -> tk.Toplevel:
        """
        Create a new table window with title and topmost attributes.

        Args:
            ct_root (tk.Tk): The root tkinter window.
            title (str): The title of the table window.

        Returns:
            tk.Toplevel: The new table window.
        """
        ct_window = tk.Toplevel(ct_root)
        ct_window.title(title)
        ct_window.attributes('-topmost', True)
        return ct_window


    def get_column_names(columns_data: List[Dict[str, Any]]) -> List[str]:
        """
        Extract column names from dataset.

        Args:
            columns_data (List[Dict[str, Any]]): The data from which to extract column names.

        Returns:
            List[str]: The list of column names.
        """
        return list(columns_data[0].keys()) if columns_data else []


    def setup_table(st_window: tk.Toplevel, st_data: List[Dict[str, Any]], st_column_names: List[str]) -> ttk.Treeview:
        """
        Set up the Treeview table inside the window.

        Args:
            st_window (tk.Toplevel): The table window.
            st_data (List[Dict[str, Any]]): The data to be displayed in the table.
            st_column_names (List[str]): The names of the columns.

        Returns:
            ttk.Treeview: The configured Treeview table.
        """
        frame = tk.Frame(st_window)
        frame.pack(expand=True, fill=tk.BOTH)
        tree = ttk.Treeview(frame, columns=column_names, show='headings')
        tree.grid(row=0, column=0, sticky='nsew')

        # Configure columns and add headings
        setup_table_columns(tree, st_column_names, st_data)

        # Add data rows to table
        add_data_to_table(tree, st_data, st_column_names)

        # Add scrollbars
        add_scrollbars(tree, frame)

        return tree


    def setup_table_columns(tree: ttk.Treeview, column_names: List[str], data: List[Dict[str, Any]]):
        """
        Set up columns for the Treeview with appropriate widths.

        Args:
            tree (ttk.Treeview): The Treeview table.
            column_names (List[str]): The names of the columns.
            data (List[Dict[str, Any]]): The data to determine column widths.
        """
        for col in column_names:
            max_length = max(len(str(row[col])) for row in data)
            max_len_col = len(col) + 5
            column_width = max(max_len_col, max_length) * PIXEL_SCALE

            tree.heading(col, text=col)
            tree.column(col, width=column_width)


    def add_data_to_table(tree: ttk.Treeview, data: List[Dict[str, Any]], column_names: List[str]):
        """
        Insert rows of data into the table.

        Args:
            tree (ttk.Treeview): The Treeview table.
            data (List[Dict[str, Any]]): The data to be inserted.
            column_names (List[str]): The names of the columns.
        """
        for row in data:
            values = [row[col] for col in column_names]
            tree.insert('', tk.END, values=values)


    def add_scrollbars(tree: ttk.Treeview, frame: tk.Frame):
        """
        Add horizontal and vertical scrollbars to the Treeview.

        Args:
            tree (ttk.Treeview): The Treeview table.
            frame (tk.Frame): The frame containing the Treeview.
        """
        scrollbar_x = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
        scrollbar_y = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)

        tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)


    def setup_row_selection(tree: ttk.Treeview, window: tk.Toplevel, column_names: List[str], selected_row: dict):
        """
        Add logic to handle row selection.

        Args:
            tree (ttk.Treeview): The Treeview table.
            window (tk.Toplevel): The table window.
            column_names (List[str]): The names of the columns.
            selected_row (dict): The dictionary to store the selected row.
        """

        def on_select(event=None):
            selected_items = tree.selection()
            if selected_items:
                item = selected_items[0]
                selected_values = tree.item(item, 'values')
                for i, col_name in enumerate(column_names):
                    selected_row[col_name] = selected_values[i]
                window.after(100, window.destroy)

        tree.bind('<Double-1>', on_select)
        tree.bind('<Return>', on_select)


    def setup_keyboard_navigation_with_horizontal_scrolling(tree: ttk.Treeview):
        """
        Add keyboard navigation (vertical + horizontal scrolling) to the Treeview.

        Args:
            tree (ttk.Treeview): The Treeview table.
        """

        def on_key(event):
            children = tree.get_children()
            if not children:
                return

            selected = tree.selection()
            index = list(children).index(selected[0]) if selected else -1

            # Vertical navigation (up and down)
            if event.keysym in ('Up', 'w') and index > 0:
                focus_row(tree, children[index])
            elif event.keysym in ('Down', 's') and index < len(children) - 1:
                focus_row(tree, children[index])

            # Horizontal scrolling (left and right)
            elif event.keysym in ('Left', 'a'):
                tree.xview_scroll(-20, "units")  # may be "pages" left-right
            elif event.keysym in ('Right', 'd'):
                tree.xview_scroll(20, "units")  # Scroll right by 20 units

        # Binding events to keys
        tree.bind('<Up>', on_key)  # Move up
        tree.bind('<Down>', on_key)  # Move down
        tree.bind('<Left>', on_key)  # Scroll left
        tree.bind('<Right>', on_key)  # Scroll right

    def focus_row(tree: ttk.Treeview, row: str):
        """
        Focus on a specific Treeview row.

        Args:
            tree (ttk.Treeview): The Treeview table.
            row (str): The row to focus on.
        """
        tree.selection_clear()
        tree.selection_set(row)
        tree.focus(row)
        tree.see(row)


    def auto_focus_first_row(tree: ttk.Treeview, data: List[Dict[str, Any]]) -> None:

        """
            Automatically focus and select the first row of the table.

            Args:
                tree (ttk.Treeview): The Treeview table.
                data (List[Dict[str, Any]]): The data in the table.
            """
        if data:
            if tree.get_children():  # Check if there is data
                first_row = tree.get_children()[0]  # Get the ID of the first row
                tree.focus(first_row)  # Set focus on the first row
                tree.selection_set(first_row)  # Select the first row
                tree.focus_set()  # Set focus on the Treeview for keyboard interaction


    def adjust_window_size_and_center(window: tk.Toplevel, column_names: List[str], tree: ttk.Treeview,
                                      root: tk.Tk) -> None:

        """
            Adjust window size based on content and center it on the screen.

            Args:
                window (tk.Toplevel): The table window.
                column_names (List[str]): The names of the columns.
                tree (ttk.Treeview): The Treeview table.
                root (tk.Tk): The root tkinter window.
            """
        window_width = min(
            sum(tree.column(col, option='width') for col in column_names),
            root.winfo_screenwidth() - DEFAULT_WINDOW_WIDTH_PADDING
        )
        window_height = min(DEFAULT_WINDOW_HEIGHT, root.winfo_screenheight() - DEFAULT_WINDOW_HEIGHT_PADDING)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height / 2 - window_height / 2)

        window.geometry(f"{window_width}x{window_height}")
        window.geometry(f"+{position_right}+{position_down}")


    def lock_main_window(window: tk.Toplevel, root: tk.Tk):
        """
        Block the main tkinter window until the table window is closed.

        Args:
            window (tk.Toplevel): The table window.
            root (tk.Tk): The root tkinter window.
        """
        window.transient(root)
        window.grab_set()
        root.wait_window(window)


    # Ensure a tkinter root window exists
    root = initialize_tkinter_root_window()

    # Create and configure table window
    window = create_table_window(root, window_title)

    if not data:
        return {}

    column_names = get_column_names(data)
    selected_row = {}

    if column_names:
        # Create Treeview and set up the table
        main_table = setup_table(window, data, column_names)

        # Add selection logic
        setup_row_selection(main_table, window, column_names, selected_row)

        # Add keyboard navigation
        setup_keyboard_navigation_with_horizontal_scrolling(main_table)

        # Auto-focus and select the first row
        auto_focus_first_row(main_table, data)

        # Resize and center the window
        adjust_window_size_and_center(window, column_names, main_table, root)

        # Set focus to Treeview
        window.after(100, lambda: main_table.focus_set())

    # Block main window until the table is closed
    lock_main_window(window, root)

    return selected_row


#======================================== get_keyword ==================================================================
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 250

def get_keyword(root, title, default_search_option="both"):
    """
    Prompt the user to enter a keyword and select search options.

    Args:
        root (tk.Tk): The root tkinter window.
        title (str): The title of the dialog window.
        default_search_option (str): The default search option. Can be "title", "description", or "both".

    Returns:
        dict: A dictionary containing the keyword and search options.
    """

    # Initial parameters
    result = {"keyword": "", "title": False, "description": False, "both": True}

    # Create a child window
    dialog = tk.Toplevel(root)
    dialog.title(title)
    center_window(dialog, root, WINDOW_WIDTH, WINDOW_HEIGHT)
    dialog.resizable(False, False)

    # Container for central placement
    main_frame = tk.Frame(dialog)
    main_frame.pack(expand=True, padx=10, pady=20)  # Center the block and add padding

    # Keyword input field
    tk.Label(main_frame, text="Enter keyword:").grid(row=0, column=0, sticky="w", pady=(0, 5))  # Label
    keyword_entry = tk.Entry(main_frame, width=30)
    keyword_entry.grid(row=1, column=0, sticky="w", pady=(0, 15))  # Input field
    keyword_entry.focus_set()

    # Radio buttons
    tk.Label(main_frame, text="Search in:").grid(row=2, column=0, sticky="w", pady=(0, 5))  # Label "Search in"
    search_option_var = tk.StringVar(value=default_search_option)
    tk.Radiobutton(main_frame, text="Title", variable=search_option_var, value="title").grid(row=3, column=0, sticky="w")
    tk.Radiobutton(main_frame, text="Description", variable=search_option_var, value="description").grid(row=4, column=0, sticky="w")
    tk.Radiobutton(main_frame, text="Both", variable=search_option_var, value="both").grid(row=5, column=0, sticky="w", pady=(0, 15))

    # Action for the "Search" button
    def submit_action():
        keyword = keyword_entry.get().strip()  # Remove extra spaces
        if not keyword:  # Input validation
            messagebox.showerror("Error", "Keyword cannot be empty or whitespace only")
            return
        result.update({
            "keyword": keyword,
            "title": search_option_var.get() == "title",
            "description": search_option_var.get() == "description",
            "both": search_option_var.get() == "both",
        })
        dialog.destroy()  # Close the window if everything is OK

    # Submit button
    tk.Button(main_frame, text="Search", command=submit_action).grid(row=6, column=0, sticky="s")

    # Bind the Enter key
    dialog.bind('<Return>', lambda event: submit_action())

    # Window settings for interaction
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    return result

#======================================== display_record ==================================================================
def display_record(root: tk.Tk, record: Dict[str, str]) -> None:
    """
    Display a database record in a tkinter window.

    Args:
        record (Dict[str, str]): A dictionary representing a database record.
    """
    padding = 30
    max_width = root.winfo_screenwidth() - 400
    max_height = root.winfo_screenheight() - 300

    # Create a child window
    dialog = tk.Toplevel(root)
    dialog.title("Selected movie:")
    dialog.resizable(True, True)

    # Create a frame for the content
    main_frame = tk.Frame(dialog)
    main_frame.pack(expand=True, fill=tk.BOTH, padx=padding, pady=padding)

    # Create a canvas for adding a scrollbar
    canvas = tk.Canvas(main_frame)
    scrollable_frame = tk.Frame(canvas)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame.bind( "<Configure>", lambda e: canvas.configure( scrollregion=canvas.bbox("all") ) )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Display the record fields and values
    row = 0
    for key, value in record.items():
        label_key = tk.Label(scrollable_frame, text=f"{key}:", anchor='w', justify='left')
        label_key.grid(row=row, column=0, sticky='w', padx=(0, padding))

        label_value = tk.Label(scrollable_frame,
                               text=value,
                               anchor='w',
                               justify='left',
                               wraplength=max_width - 4*padding # wrap long string
                               )
        label_value.grid(row=row,
                         column=1,
                         sticky='w'
                         )

        row += 1

    def close_window(event=None):
        dialog.destroy()

    # Add an "Ok" button
    ok_button = tk.Button(scrollable_frame,
                          text="Ok",
                          width=10,     # button width
                          bg='#D3D3D3', # background color (LightBlue)
                          # bg="#add8e6", # background color (LightBlue)
                          command=close_window)
    ok_button.grid(row=row,
                   column=0,
                   columnspan=2,
                   pady=(padding, 0),
                   sticky="s")
    dialog.bind('<Return>', close_window)

    # Adjust window size based on content
    dialog.update_idletasks()
    content_height = scrollable_frame.winfo_reqheight() + 2 * padding
    content_width = scrollable_frame.winfo_reqwidth() + 2 * padding + scrollbar.winfo_reqwidth()

    window_width = min(content_width, max_width)
    window_height = min(content_height, max_height)

    if content_height > max_height or content_width > max_width:
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    else:
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack_forget()

    dialog.geometry(f"{window_width}x{window_height}")
    center_window(dialog, root, window_width, window_height)

    # Window settings for interaction
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

#======================================== center_window ==================================================================
def center_window(window, root, width, height):
    """
    Calculate and set the window position to the center of the screen.

    Args:
        window (tk.Toplevel): The window to be centered.
        root (tk.Tk): The root tkinter window.
        width (int): The width of the window.
        height (int): The height of the window.
    """
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = (screen_width // 2) - (width // 2)
    position_y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{position_x}+{position_y}")