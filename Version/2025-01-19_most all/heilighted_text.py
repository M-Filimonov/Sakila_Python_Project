import tkinter as tk
from tkinter import ttk
from typing import Dict


def highlight_text_widget(text_widget: tk.Text, text: str, search: str, tag_name: str) -> None:
    """
    Insert text into Text widget and highlight all occurrences of the search string.

    Args:
        text_widget (tk.Text): The Text widget where the text is inserted.
        text (str): The text to insert into the Text widget.
        search (str): The search string to highlight.
        tag_name (str): The name of the tag used for highlighting.
    """
    text_widget.insert("1.0", text)
    if search:
        start_idx = "1.0"
        while True:
            start_idx = text_widget.search(search, start_idx, stopindex=tk.END)
            if not start_idx:
                break
            end_idx = f"{start_idx}+{len(search)}c"
            text_widget.tag_add(tag_name, start_idx, end_idx)
            start_idx = end_idx


def display_record(root: tk.Tk, record: Dict[str, str], highlight_terms: Dict[str, str]) -> None:
    """
    Display a database record in a tkinter window with highlighted search terms.

    Args:
        root (tk.Tk): The root tkinter window.
        record (Dict[str, str]): A dictionary representing a database record.
        highlight_terms (Dict[str, str]): A dictionary where keys are field names and values are search strings to highlight.
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
    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Define a common font
    common_font = ('Arial', 9)

    # Display the record fields and values
    row = 0
    for key, value in record.items():
        label_key = tk.Label(scrollable_frame,
                             text=f"{key}:",
                             anchor='w',
                             justify='left',
                             font=common_font
                             )
        label_key.grid(row=row, column=0, sticky='nw', padx=(0, padding))

        # Вычисляем нужное количество строк для Text-виджета
        lines = value.count('\n') + 1  # Считаем количество строк текста (по переносам)
        avg_char_per_line = 50  # Среднее количество символов в строке
        lines += len(value) // avg_char_per_line  # Учитываем длину текста
        lines = min(lines, 10)  # Ограничиваем максимальную высоту (10 строк)

        # Создаём Text-виджет с высотой, зависящей от текста
        text_widget = tk.Text(scrollable_frame,
                              wrap="word",
                              height=lines,
                              bg=dialog.cget('bg'),
                              bd=0,
                              font=common_font
                              )
        text_widget.tag_configure("highlight", foreground="blue")
        if key in highlight_terms:
            highlight_text_widget(text_widget, value, highlight_terms[key], "highlight")
        else:
            text_widget.insert("1.0", value)
        text_widget.configure(state='disabled')  # Делаем Text виджет только для чтения
        text_widget.grid(row=row, column=1, sticky='w', padx=(0, padding))

        row += 1

    def close_window(event=None):
        dialog.destroy()
        root.destroy()  # Close the main window

    # Add an "Ok" button
    ok_button = tk.Button(scrollable_frame, text="Ok", width=10, bg='#D3D3D3', command=close_window,
                          # font=common_font
                          )
    ok_button.grid(row=row, column=0, columnspan=2, pady=(padding, 0), sticky="s")
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


def center_window(window, root, width, height):
    """
    Calculate and set the window position to the center of the screen.

    Args:
        window (tk.Toplevel): The window to be centered.
        root (tk.Tk): The root tkinter window.
    """
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_x = (screen_width // 2) - (width // 2)
    position_y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{position_x}+{position_y}")


# Example usage
if __name__ == '__main__':
    root = tk.Tk()
    record = {
        "Title": "Inception",
        "Description": "1. A thief who steals corporate secrets through the use of dream-sharing technology. 2 . A thief who steals corporate secrets through the use of dream-sharing technology",
        "Year": "2010"
    }
    highlight_terms = {
        "Title": "Inception",
        "Description": "dream"
    }

    display_record(root, record, highlight_terms)

    root.mainloop()
