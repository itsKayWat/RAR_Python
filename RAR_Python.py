import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import datetime
from PIL import Image, ImageTk
import mimetypes
import shutil

class DarkArchiver:
    def __init__(self):
        # Initialize main window
        self.root = tk.Tk()
        self.root.title("Dark Archiver")
        
        # Set window size
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Updated emerald theme colors
        self.colors = {
            'bg': '#0A1F1C',           # Dark emerald background
            'fg': '#00FF9D',           # Bright emerald text
            'accent': '#FFE162',       # Yellow accent
            'button_bg': '#0C2925',    # Slightly lighter emerald
            'hover': '#133B36',        # Hover state
            'selected': '#1A4D47',     # Selected state
            'error': '#FF4444',        # Error red
            'success': '#44FF44',      # Success green
            'warning': '#FFB302',      # Warning yellow
            'info': '#3498db'          # Info blue
        }
        
        # Add custom styles
        self.setup_styles()
        
        # Set background color
        self.root.configure(bg=self.colors['bg'])
        
        # Initialize storage
        self.file_paths = {}
        
        # Initialize preview settings
        self.show_preview = True
        self.preview_size = (200, 200)
        
        # Add search functionality
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        
        # Create GUI elements
        self.create_gui()
        self.create_menu()
        self.create_search_bar()
        self.create_preview_panel()

    def setup_styles(self):
        # Configure Treeview style
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure Treeview colors
        style.configure(
            "Treeview",
            background=self.colors['bg'],
            foreground=self.colors['fg'],
            fieldbackground=self.colors['bg'],
            borderwidth=0
        )
        
        # Configure Treeview selected colors
        style.map(
            "Treeview",
            background=[('selected', self.colors['selected'])],
            foreground=[('selected', self.colors['accent'])]
        )
        
        # Configure Scrollbar style
        style.configure(
            "Custom.Vertical.TScrollbar",
            background=self.colors['button_bg'],
            bordercolor=self.colors['bg'],
            arrowcolor=self.colors['fg'],
            troughcolor=self.colors['bg']
        )

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Add Files...", command=self.add_files)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Select All", command=self.select_all)
        edit_menu.add_command(label="Delete", command=self.delete_files)

    def create_gui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create toolbar
        toolbar = tk.Frame(main_frame, bg=self.colors['bg'])
        toolbar.pack(fill='x', pady=5)
        
        # Update button styles
        button_style = {
            'bg': self.colors['button_bg'],
            'fg': self.colors['fg'],
            'activebackground': self.colors['hover'],
            'activeforeground': self.colors['accent'],
            'relief': 'flat',
            'bd': 0,
            'padx': 15,
            'pady': 5,
            'font': ('Arial', 9),
            'cursor': 'hand2'
        }
        
        # Add education-themed icons
        buttons = [
            ("📚 Add Files", self.add_files),
            ("📝 Edit", self.edit_files),
            ("📋 Copy", self.copy_files),
            ("📤 Export", self.export_files),
            ("🗑 Delete", self.delete_files)
        ]
        
        for text, command in buttons:
            btn = tk.Button(toolbar, text=text, command=command, **button_style)
            btn.pack(side='left', padx=2)
            
            # Add hover effect
            btn.bind('<Enter>', lambda e, b=btn: self.on_button_hover(b))
            btn.bind('<Leave>', lambda e, b=btn: self.on_button_leave(b))
        
        # Create file list
        self.file_list = ttk.Treeview(
            main_frame,
            columns=("Size", "Type", "Modified"),
            selectmode="extended"
        )
        
        # Configure columns
        self.file_list.heading("#0", text="Name")
        self.file_list.heading("Size", text="Size")
        self.file_list.heading("Type", text="Type")
        self.file_list.heading("Modified", text="Modified")
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            main_frame, 
            orient="vertical", 
            command=self.file_list.yview
        )
        self.file_list.configure(yscrollcommand=scrollbar.set)
        
        # Pack list and scrollbar
        self.file_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Status bar
        self.status = tk.Label(
            self.root,
            text="Ready",
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            anchor='w'
        )
        self.status.pack(fill='x', side='bottom', pady=2)

    def create_search_bar(self):
        search_frame = tk.Frame(self.root, bg=self.colors['bg'])
        search_frame.pack(fill='x', padx=5, pady=2)
        
        # Search icon/label
        tk.Label(
            search_frame,
            text="🔍",
            bg=self.colors['bg'],
            fg=self.colors['fg']
        ).pack(side='left', padx=2)
        
        # Search entry
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg']
        )
        self.search_entry.pack(side='left', fill='x', expand=True)
        
        # Clear search button
        tk.Button(
            search_frame,
            text="✕",
            command=self.clear_search,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            relief='flat',
            width=2
        ).pack(side='left', padx=2)

    def create_preview_panel(self):
        self.preview_frame = tk.Frame(self.root, bg=self.colors['bg'], width=250)
        self.preview_frame.pack(side='right', fill='y', padx=5)
        
        # Preview header with close button
        header_frame = tk.Frame(self.preview_frame, bg=self.colors['bg'])
        header_frame.pack(fill='x', pady=5)
        
        tk.Label(
            header_frame,
            text="Preview",
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            font=('Arial', 10, 'bold')
        ).pack(side='left', padx=5)
        
        tk.Button(
            header_frame,
            text="✕",
            command=self.toggle_preview,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            relief='flat',
            cursor='hand2'
        ).pack(side='right', padx=5)
        
        # Preview content
        self.preview_content = tk.Label(
            self.preview_frame,
            text="No file selected",
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            wraplength=200
        )
        self.preview_content.pack(fill='both', expand=True, padx=5, pady=5)
        
        # File information
        self.file_info = tk.Text(
            self.preview_frame,
            bg=self.colors['button_bg'],
            fg=self.colors['fg'],
            height=8,
            width=30,
            relief='flat',
            state='disabled'
        )
        self.file_info.pack(fill='x', padx=5, pady=5)
        
        # Bind selection change
        self.file_list.bind('<<TreeviewSelect>>', self.update_preview)

    def update_preview(self, event=None):
        selected = self.file_list.selection()
        if not selected:
            self.clear_preview()
            return
        
        file_path = self.file_paths[selected[0]]
        self.show_file_preview(file_path)

    def show_file_preview(self, file_path):
        try:
            # Get file info
            file_stats = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # Update file info
            info_text = f"Name: {os.path.basename(file_path)}\n"
            info_text += f"Size: {self.format_size(file_stats.st_size)}\n"
            info_text += f"Type: {mime_type or 'Unknown'}\n"
            info_text += f"Modified: {datetime.datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M')}\n"
            
            self.file_info.config(state='normal')
            self.file_info.delete(1.0, tk.END)
            self.file_info.insert(tk.END, info_text)
            self.file_info.config(state='disabled')
            
            # Show preview based on file type
            if mime_type and mime_type.startswith('image/'):
                self.show_image_preview(file_path)
            else:
                self.preview_content.config(
                    text="No preview available\nfor this file type",
                    image=''
                )
                
        except Exception as e:
            self.preview_content.config(
                text=f"Error loading preview:\n{str(e)}",
                image=''
            )

    def show_image_preview(self, file_path):
        try:
            image = Image.open(file_path)
            image.thumbnail(self.preview_size)
            photo = ImageTk.PhotoImage(image)
            
            self.preview_content.config(image=photo)
            self.preview_content.image = photo  # Keep reference
            
        except Exception as e:
            self.preview_content.config(
                text=f"Error loading image:\n{str(e)}",
                image=''
            )

    def clear_preview(self):
        self.preview_content.config(image='', text="No file selected")
        self.file_info.config(state='normal')
        self.file_info.delete(1.0, tk.END)
        self.file_info.config(state='disabled')

    def toggle_preview(self):
        if self.show_preview:
            self.preview_frame.pack_forget()
        else:
            self.preview_frame.pack(side='right', fill='y', padx=5)
        self.show_preview = not self.show_preview

    def on_search_change(self, *args):
        self.filter_files()

    def clear_search(self):
        self.search_var.set("")
        self.search_entry.focus()

    def filter_files(self):
        search_term = self.search_var.get().lower()
        
        # Show all items if search is empty
        if not search_term:
            for item in self.file_paths:
                self.file_list.reattach(item, '', 'end')
            return
        
        # Filter items
        for item in self.file_paths:
            item_text = self.file_list.item(item)['text'].lower()
            if search_term in item_text:
                self.file_list.reattach(item, '', 'end')
            else:
                self.file_list.detach(item)

    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    def add_files(self):
        files = filedialog.askopenfilenames()
        for file in files:
            name = os.path.basename(file)
            size = os.path.getsize(file)
            file_type = os.path.splitext(name)[1]
            modified = datetime.datetime.fromtimestamp(os.path.getmtime(file))
            
            item = self.file_list.insert(
                "",
                "end",
                text=name,
                values=(
                    f"{size/1024:.1f} KB",
                    file_type,
                    modified.strftime("%Y-%m-%d %H:%M")
                )
            )
            self.file_paths[item] = file
        
        if files:
            self.status.config(text=f"Added {len(files)} files")

    def select_all(self):
        for item in self.file_list.get_children():
            self.file_list.selection_add(item)

    def delete_files(self):
        selected = self.file_list.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select files to delete")
            return
        
        for item in selected:
            self.file_list.delete(item)
            if item in self.file_paths:
                del self.file_paths[item]
        
        self.status.config(text=f"Removed {len(selected)} files")

    def on_button_hover(self, button):
        button.config(
            bg=self.colors['hover'],
            fg=self.colors['accent']
        )

    def on_button_leave(self, button):
        button.config(
            bg=self.colors['button_bg'],
            fg=self.colors['fg']
        )

    def edit_files(self):
        selected = self.file_list.selection()
        if not selected:
            self.show_message("Please select files to edit", "warning")
            return
            
        # Add edit functionality here
        self.show_message("Edit functionality coming soon", "info")

    def copy_files(self):
        selected = self.file_list.selection()
        if not selected:
            self.show_message("Please select files to copy", "warning")
            return
            
        dest_dir = filedialog.askdirectory(title="Select Destination")
        if not dest_dir:
            return
            
        try:
            copied = 0
            for item in selected:
                src_path = self.file_paths[item]
                dest_path = os.path.join(dest_dir, os.path.basename(src_path))
                shutil.copy2(src_path, dest_path)
                copied += 1
                
            self.show_message(f"Copied {copied} files successfully", "success")
            
        except Exception as e:
            self.show_message(f"Error copying files: {str(e)}", "error")

    def export_files(self):
        selected = self.file_list.selection()
        if not selected:
            self.show_message("Please select files to export", "warning")
            return
            
        export_dir = filedialog.askdirectory(title="Select Export Location")
        if not export_dir:
            return
            
        try:
            exported = 0
            for item in selected:
                src_path = self.file_paths[item]
                dest_path = os.path.join(export_dir, os.path.basename(src_path))
                shutil.copy2(src_path, dest_path)
                exported += 1
                
            self.show_message(f"Exported {exported} files successfully", "success")
            
        except Exception as e:
            self.show_message(f"Error exporting files: {str(e)}", "error")

    def show_message(self, message, message_type="info"):
        self.status.config(
            text=message,
            fg=self.colors[message_type]
        )
        
        # Reset status after 3 seconds
        self.root.after(3000, lambda: self.status.config(
            text="Ready",
            fg=self.colors['fg']
        ))

    def create_context_menu(self):
        self.context_menu = tk.Menu(
            self.root,
            tearoff=0,
            bg=self.colors['bg'],
            fg=self.colors['fg'],
            activebackground=self.colors['hover'],
            activeforeground=self.colors['accent']
        )
        
        self.context_menu.add_command(label="📋 Copy", command=self.copy_files)
        self.context_menu.add_command(label="📤 Export", command=self.export_files)
        self.context_menu.add_command(label="📝 Edit", command=self.edit_files)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑 Delete", command=self.delete_files)
        
        # Bind right-click to show context menu
        self.file_list.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def run(self):
        self.root.mainloop()

def main():
    app = DarkArchiver()
    app.run()

if __name__ == "__main__":
    main()