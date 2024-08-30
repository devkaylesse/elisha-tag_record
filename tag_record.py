import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from datetime import datetime
import requests
import sys 
import os

#---------VARIABLES-------------#

toast_queue = []
is_showing = False
toast_windows = []

#--------VARIABLES-------------#

# -------FUNCTIONS-----------#

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller. """
    try:
        # PyInstaller creates a temp folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def add_entry_placeholder(entry_widget, placeholder_text):
    entry_widget.insert(0, placeholder_text)
    entry_widget.bind("<FocusIn>", lambda event: on_entry_focus_in(event, placeholder_text))
    entry_widget.bind("<FocusOut>", lambda event: on_entry_focus_out(event, placeholder_text))

def on_entry_focus_in(event, placeholder_text):
    if event.widget.get() == placeholder_text:
        event.widget.delete(0, tk.END)
        event.widget.config(foreground="black")  # Normal text color

def on_entry_focus_out(event, placeholder_text):
    if event.widget.get() == "":
        event.widget.insert(0, placeholder_text)
        event.widget.config(foreground="gray")  # Placeholder text color

def on_closing():
    """Handle the cleanup when the window is closed."""
    print("Application is closing, performing cleanup...")
    root.destroy()

def show_toast(root, title, message, duration=2000, position="top-right", bootstyle="info", icon="", alpha=0.9, bg_color=None, width=200):
    global is_showing
    # If no bg_color is provided, use default based on bootstyle
    if bg_color is None:
        colors = {"success": "#28a745", "danger": "#dc3545", "info": "#17a2b8"}
        bg_color = colors.get(bootstyle, "#17a2b8")
    toast_queue.append((title, message, duration, position, bootstyle, icon, alpha, bg_color, width))
    if not is_showing:
        _show_next_toast(root)

def _show_next_toast(root):
    global is_showing
    if not toast_queue:
        is_showing = False
        return

    is_showing = True
    title, message, duration, position, bootstyle, icon, alpha, bg_color, width = toast_queue.pop(0)

    # Create toast window
    toast = tk.Toplevel(root)
    toast.overrideredirect(True)
    toast.attributes('-topmost', True)
    toast.attributes('-alpha', alpha)
    # toast.configure(bg=bg_color)
    
    # Calculate position based on existing toast windows
    x = root.winfo_screenwidth() - width - 20 if position == "top-right" else 20
    y = 20 + sum(window.winfo_height() + 10 for window in toast_windows)  # +10 for spacing

    # Create the frame for the toast content
    frame = tk.Frame(toast)
    frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Configure grid columns and rows
    frame.grid_columnconfigure(1, weight=1)

    # Add icon if provided
    if icon:
        # Use resource_path to get the correct path to the icon
        icon_path = resource_path(icon)
        if os.path.isfile(icon_path):
            # Load the image
            icon_img = tk.PhotoImage(file=icon_path)

            # Resize the image by reducing the size (e.g., by a factor of 5)
            icon_img = icon_img.subsample(18, 18)  # Adjust the factor as needed

            # Create the label with the resized image
            icon_label = tk.Label(frame, image=icon_img, bg=bg_color)
            icon_label.image = icon_img  # Keep a reference to avoid garbage collection
            icon_label.grid(row=0, column=0, padx=(5, 5), sticky="nsw")

    # Create a frame for text content
    text_frame = tk.Frame(frame, bg=bg_color)
    text_frame.grid(row=0, column=1, sticky="nsew")

    # Add title and message labels with wraplength
    title_label = tk.Label(text_frame, text=title, font=("Helvetica", 12, "bold"), bg=bg_color, wraplength=width-70)
    title_label.grid(row=0, column=0, sticky="w",padx=(0, 20))

    message_label = tk.Label(text_frame, text=message, font=("Helvetica", 10), bg=bg_color, wraplength=width-70, justify="left")
    message_label.grid(row=1, column=0, sticky="w",padx=(0, 20))

    # Force update geometry to get the correct height after adding text
    toast.update_idletasks()
    new_height = toast.winfo_reqheight()  # Get the correct required height
    toast.geometry(f"{width}x{new_height}+{x}+{y}")

    # Add a close button
    close_button = tk.Button(toast, text="✖", font=("Helvetica", 10), command=lambda: _remove_toast(root, toast), bd=0, relief="flat")
    close_button.place(x=width-30, y=5, width=25, height=25)  # Adjust placement and size

    toast_windows.append(toast)

    # Schedule the toast to be removed
    root.after(duration, lambda: _remove_toast(root, toast))

def _remove_toast(root, toast):
    global is_showing
    if toast in toast_windows:
        toast_windows.remove(toast)
    toast.destroy()
    
    # Move remaining toasts up
    for i, window in enumerate(toast_windows):
        x, _ = map(int, window.geometry().split("+")[1:])
        new_y = 20 + i * (window.winfo_height() + 10)
        window.geometry(f"+{x}+{new_y}")
    
    if not toast_queue:
        is_showing = False
    else:
        _show_next_toast(root)

# Get page ID from Page Name
def get_page_id(page_name, access_token):
    base_url = f"https://botcake.io/api/v1/pages?access_token={access_token}"
    try:

        response = requests.get(base_url)
        if response.status_code == 200:
            data = response.json()
            pages = data.get("categorized", {}).get("activated", [])
            for page in pages:
                if page["name"].lower() == page_name.lower():
                    page_id = page["id"]  # Set PAGE_ID value
                    page_name = page["name"]  # Set PAGE_ID value
                    return page_id, page_name
                elif page["id"] == page_name:
                    page_id = page['id']
                    page_name = page['name']
                    return page_id, page_name

            # message = f"{page_name} not Found\n"
            page_id = False
            show_toast(root, "Failed", "Can't generate data. Page not found.", duration=5000, bootstyle="danger", icon="img/error_icon.png", bg_color="#F44336", width=350)

            return page_id, False
        else:
            # message = f"Failed to retrieve data. Status code: {response.status_code}\n"
            show_toast(root, "Failed", "Failed to Retreive Data. Please check your Page Name, Access Token , API or Internet Connection.", duration=5000, bootstyle="danger", icon="img/error_icon.png", bg_color="#F44336", width=350)

    except Exception as e:
        # message = f"An error occurred: {e} \n"
        show_toast(root, "Failed", "Failed to Retreive Data. Please check your Page Name, Access Token , API or Internet Connection.", duration=5000, bootstyle="danger", icon="img/error_icon.png", bg_color="#F44336", width=350)


def get_tag_data():
    page_name = page_name_entry.get()
    access_token = access_token_entry.get()
    page_id, page_id_name = get_page_id(page_name, access_token)
    
    tag_url = f"https://botcake.io/api/v1/pages/{page_id}/tags?access_token={access_token}"

    tag_response = requests.get(tag_url)
    if tag_response.status_code == 200:
        data = tag_response.json()
        # Process and display the data in the Treeview
        update_treeview(data)

        show_toast(root, "Success!", "Tag Records Successfully Generated!", duration=4000, bootstyle="success", icon="img/success_icon.png", bg_color="#4CAF50", width=350)

    else:
        print("Failed to retrieve data:", tag_response.status_code)

def update_treeview(data):
    # Clear existing rows
    for row in tag_tree.get_children():
        tag_tree.delete(row)

    # Process and add new data
    sequences = data.get("sequences", [])
    for sequence in sequences:
        tag_tree.insert("", tk.END, values=(sequence["name"], sequence["subscribers"]))

def search_tags():
    search_term = search_entry.get().strip().lower()
    
    # Clear existing rows
    for row in tag_tree.get_children():
        tag_tree.delete(row)
    
    # Fetch the data again (or use a cached version if available)
    page_name = page_name_entry.get()
    access_token = access_token_entry.get()
    page_id, _ = get_page_id(page_name, access_token)
    
    if page_id:
        tag_url = f"https://botcake.io/api/v1/pages/{page_id}/tags?access_token={access_token}"
        tag_response = requests.get(tag_url)
        
        if tag_response.status_code == 200:
            data = tag_response.json()
            sequences = data.get("sequences", [])
            
            # Filter and display data
            for sequence in sequences:
                if search_term in sequence["name"].lower():
                    tag_tree.insert("", tk.END, values=(sequence["name"], sequence["subscribers"]))
        else:
            # print("Failed to retrieve data:", tag_response.status_code)
            show_toast(root, "Failed", "Failed to retrieve data. Please try again.", duration=4000, bootstyle="danger", icon="img/error_icon.png", bg_color="#F44336", width=350)
    else:
        show_toast(root, "Error", "Invalid Page ID or Access Token.", duration=4000, bootstyle="danger", icon="img/error_icon.png", bg_color="#F44336", width=350)
        
# --------FUNCTIONS-----------#

# -------UI CONFIGURATION-----------#

root = tk.Tk()
root.title("IT: Tag Record App")
root.geometry("600x700")  # Set a fixed window size

style = ttk.Style("elisha_theme8")
style.configure("CustomDisabled.TEntry")
style.configure("CustomDisabled.TCombobox")
style.map("CustomDisabled.TCombobox",
          fieldbackground=[("disabled", "#D3D3D3")],
          foreground=[("disabled", "gray")])

style.map("CustomDisabled.TEntry",
          fieldbackground=[("disabled", "#D3D3D3")],
          foreground=[("disabled", "gray")])

style.configure("Treeview.Heading",
                font=('Arial', 10, 'bold'),  # Set font to Arial, 10pt, bold
                background='black',          # Set background color to black
                foreground='white') 

form = ttk.Frame(root, padding="10")
form.grid(row=0, column=0, sticky="nsew")  # Corrected line

# Grid Configuration for Resizing
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
form.grid_rowconfigure(2, weight=1)
form.grid_columnconfigure(0, weight=1)

# Title Frame
title_frame = ttk.Frame(form)
title_frame.grid(row=0, column=0, sticky="ew", pady=(10, 0))

# Image Title and Logo
icon_path = resource_path("img/logo.ico")
root.iconbitmap(icon_path)

image_path = resource_path("img/name_logo.png")
image = tk.PhotoImage(file=image_path)
resized_image = image.subsample(5, 5)

image_label = ttk.Label(title_frame, image=resized_image)
image_label.grid(row=0, column=0, padx=(10, 20), sticky=tk.W)

# Date Label
today_date = datetime.today().strftime("%A, %B %d, %Y")
date_label = ttk.Label(title_frame, text=f"Today is: {today_date}", font=("Helvetica", 10, "bold"))
date_label.grid(row=0, column=1, sticky=tk.E, padx=20)

# Add buttons
entry_frame = ttk.Frame(form)
entry_frame.grid(row=1, column=0, pady=10, sticky="ew")

enter_frame = ttk.Frame(entry_frame)
enter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

page_name_entry = ttk.Entry(enter_frame, width=25)
page_name_entry.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=1, padx=(0, 5))

# Add placeholder text
placeholder_text = "Enter your Page ID here..."
add_entry_placeholder(page_name_entry, placeholder_text)

# Add Access Token entry with placeholder
access_token_entry = ttk.Entry(enter_frame, width=30)
access_token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=1)

# Add placeholder text for Access Token
access_token_placeholder = "Enter your Access Token here..."
add_entry_placeholder(access_token_entry, access_token_placeholder)

generate_button = ttk.Button(enter_frame, text="Generate Data", bootstyle="primary",command=get_tag_data)
generate_button.grid(row=0, column=2, padx=5)

# Search Bar
search_frame = ttk.Frame(entry_frame)
search_frame.grid(row=1, column=0, padx=10,  sticky="ew" )

search_entry = ttk.Entry(search_frame, width=35)
search_entry.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=1, padx=(0, 5))
search_entry.bind("<Return>", lambda event: search_tags())

# Add placeholder text in seacrh bar
placeholder_text = "Enter Search Tag Name..."
add_entry_placeholder(search_entry, placeholder_text)

# Search Button
search_button = ttk.Button(search_frame, text="Search Tag", bootstyle="danger", command=search_tags)
search_button.grid(row=0, column=1, padx=5)

# Create a frame to hold the Treeview and scrollbars
table_frame = ttk.Frame(form)
table_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

# Create vertical scrollbar
vsb = ttk.Scrollbar(table_frame, orient="vertical")
vsb.grid(row=0, column=1, sticky="ns")

# Create horizontal scrollbar
hsb = ttk.Scrollbar(table_frame, orient="horizontal")
hsb.grid(row=1, column=0, sticky="ew")

# Create Treeview
columns = ("Tag Name", "Total Tags")
tag_tree = ttk.Treeview(table_frame, columns=columns, show='headings', yscrollcommand=vsb.set, xscrollcommand=hsb.set)

# Configure scrollbars
vsb.config(command=tag_tree.yview)
hsb.config(command=tag_tree.xview)

# Set column headings and widths
for col in columns:
    tag_tree.heading(col, text=col)
    tag_tree.column(col, width=200, anchor="center")  # Center align the text

tag_tree.grid(row=0, column=0, sticky="nsew")

# Allow table to expand
table_frame.grid_rowconfigure(0, weight=1)
table_frame.grid_columnconfigure(0, weight=1)

# Bind the close event to the cleanup function
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()

