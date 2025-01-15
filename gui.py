import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from typing import List, Dict, Any

#======================================== display_table ==================================================================
PIXEL_SCALE = 8
DEFAULT_WINDOW_WIDTH_PADDING = 500
DEFAULT_WINDOW_HEIGHT_PADDING = 150
DEFAULT_WINDOW_WIDTH = 400
DEFAULT_WINDOW_HEIGHT = 400
TABLE_ROW_HEIGHT = 100  # Default row height for calculation


def display_table(data: List[Dict[str, Any]], window_title: str) -> Dict[str, Any]:
    """Display a table using tkinter Treeview."""
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
        tree = setup_table(window, data, column_names)

        # Add selection logic
        setup_row_selection(tree, window, column_names, selected_row)

        # Add keyboard navigation
        setup_keyboard_navigation_with_horizontal_scrolling(tree)

        # Auto-focus and select the first row
        auto_focus_first_row(tree, data)

        # Resize and center the window
        adjust_window_size_and_center(window, column_names, tree, root)

        # Set focus to Treeview
        window.after(100, lambda: tree.focus_set())

    # Block main window until the table is closed
    lock_main_window(window, root)
    return selected_row


def initialize_tkinter_root_window() -> tk.Tk:
    """Returns root tkinter window, creates one if not set."""
    if not tk._default_root:
        root = tk.Tk()
        root.withdraw()
    else:
        root = tk._default_root
    return root


def create_table_window(root: tk.Tk, title: str) -> tk.Toplevel:
    """Create a new table window with title and topmost attributes."""
    window = tk.Toplevel(root)
    window.title(title)
    window.attributes('-topmost', True)
    return window


def get_column_names(data: List[Dict[str, Any]]) -> List[str]:
    """Extract column names from dataset."""
    return list(data[0].keys()) if data else []


def setup_table(window: tk.Toplevel, data: List[Dict[str, Any]], column_names: List[str]) -> ttk.Treeview:
    """Set up the Treeview table inside the window."""
    frame = tk.Frame(window)
    frame.pack(expand=True, fill=tk.BOTH)
    tree = ttk.Treeview(frame, columns=column_names, show='headings')
    tree.grid(row=0, column=0, sticky='nsew')

    # Configure columns and add headings
    setup_table_columns(tree, column_names, data)

    # Add data rows to table
    add_data_to_table(tree, data, column_names)

    # Add scrollbars
    add_scrollbars(tree, frame)

    return tree


def setup_table_columns(tree: ttk.Treeview, column_names: List[str], data: List[Dict[str, Any]]):
    """Set up columns for the Treeview with appropriate widths."""
    for col in column_names:
        max_length = max(len(str(row[col])) for row in data)
        max_len_col = len(col)+5
        column_width = max(max_len_col, max_length) * PIXEL_SCALE

        tree.heading(col, text=col)
        tree.column(col, width=column_width)


def add_data_to_table(tree: ttk.Treeview, data: List[Dict[str, Any]], column_names: List[str]):
    """Insert rows of data into the table."""
    for row in data:
        values = [row[col] for col in column_names]
        tree.insert('', tk.END, values=values)


def add_scrollbars(tree: ttk.Treeview, frame: tk.Frame):
    """Add horizontal and vertical scrollbars to the Treeview."""
    scrollbar_x = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    scrollbar_y = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)

    tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)
    scrollbar_x.grid(row=1, column=0, sticky='ew')
    scrollbar_y.grid(row=0, column=1, sticky='ns')

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)


def setup_row_selection(tree: ttk.Treeview, window: tk.Toplevel, column_names: List[str], selected_row: dict):
    """Add logic to handle row selection."""

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
    """Add keyboard navigation (vertical + horizontal scrolling) to the Treeview."""

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
    """Focus on a specific Treeview row."""
    tree.selection_clear()
    tree.selection_set(row)
    tree.focus(row)
    tree.see(row)


def auto_focus_first_row(tree: ttk.Treeview, data: List[Dict[str, Any]]):
    """Automatically focus and select the first row of the table."""
    if data:
       if tree.get_children():  # Проверяем, есть ли данные
            first_row = tree.get_children()[0]  # Получаем ID первой строки
            tree.focus(first_row)  # Устанавливаем фокус на первую строку
            tree.selection_set(first_row)  # Выделяем первую строку
            tree.focus_set()  # Передаем фокус самому Treeview для работы клавиатуры

def adjust_window_size_and_center(window: tk.Toplevel, column_names: List[str], tree: ttk.Treeview, root: tk.Tk):
    """Adjust window size based on content and center it on the screen."""
    window_width = min(
        sum(tree.column(col, option='width') for col in column_names),
        root.winfo_screenwidth() - DEFAULT_WINDOW_WIDTH_PADDING
    )
    window_height = min(DEFAULT_WINDOW_HEIGHT, root.winfo_screenheight() -DEFAULT_WINDOW_HEIGHT_PADDING)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height / 2 - window_height / 2)

    window.geometry(f"{window_width}x{window_height}")
    window.geometry(f"+{position_right}+{position_down}")


def lock_main_window(window: tk.Toplevel, root: tk.Tk):
    """Block the main tkinter window until the table window is closed."""
    window.transient(root)
    window.grab_set()
    root.wait_window(window)

#======================================== get_keyword ==================================================================
WINDOW_WIDTH = 300
WINDOW_HEIGHT = 250


def get_keyword(root, title, default_search_option="both"):
    # Начальные параметры
    result = {"keyword": "", "title": False, "description": False, "both": True}

    # Создаём подчинённое окно
    dialog = tk.Toplevel(root)
    dialog.title(title)
    center_window(dialog, root, WINDOW_WIDTH, WINDOW_HEIGHT)
    dialog.resizable(False, False)

    # Контейнер для центрального размещения
    main_frame = tk.Frame(dialog)
    main_frame.pack(expand=True, padx=10, pady=20)  # Центрируем блок и добавляем внешние отступы

    # Поле ввода ключевого слова
    tk.Label(main_frame, text="Enter keyword:").grid(row=0, column=0, sticky="w", pady=(0, 5))  # Метка
    keyword_entry = tk.Entry(main_frame, width=30)
    keyword_entry.grid(row=1, column=0, sticky="w", pady=(0, 15))  # Поле ввода
    keyword_entry.focus_set()

    # Радиокнопки
    tk.Label(main_frame, text="Search in:").grid(row=2, column=0, sticky="w", pady=(0, 5))  # Метка "Search in"
    search_option_var = tk.StringVar(value=default_search_option)
    tk.Radiobutton(main_frame, text="Title", variable=search_option_var, value="title").grid(row=3, column=0,
                                                                                             sticky="w")
    tk.Radiobutton(main_frame, text="Description", variable=search_option_var, value="description").grid(row=4,
                                                                                                         column=0,
                                                                                                         sticky="w")
    tk.Radiobutton(main_frame, text="Both", variable=search_option_var, value="both").grid(row=5, column=0, sticky="w",
                                                                                           pady=(0, 15))

    # Действие на кнопку "Search"
    def submit_action():
        keyword = keyword_entry.get().strip()  # Удаляем лишние пробелы
        if not keyword:  # Проверка ввода
            messagebox.showerror("Error", "Keyword cannot be empty or whitespace only")
            return
        result.update({
            "keyword": keyword,
            "title": search_option_var.get() == "title",
            "description": search_option_var.get() == "description",
            "both": search_option_var.get() == "both",
        })
        dialog.destroy()  # Закрытие окна, если всё в порядке

    # Кнопка Submit
    tk.Button(main_frame, text="Search", command=submit_action).grid(row=6, column=0, sticky="s")

    # Привязка клавиши Enter
    dialog.bind('<Return>', lambda event: submit_action())

    # Настройка окон для взаимодействия
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    return result



def center_window(window, root, width, height):
    """Рассчитывает и устанавливает положение окна по центру экрана."""
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = (screen_width // 2) - (width // 2)
    position_y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{position_x}+{position_y}")

