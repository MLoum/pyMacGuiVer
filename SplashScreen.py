import Tkinter as tk
import ttk


class SplashScreen():

    def __init__(self, root):
        self.root = root
        self.create_widget()
        self.top_level.deiconify()

    def create_widget(self):
        self.top_level = tk.Toplevel()
        self.top_level.title("Loading device")

        self.txt = tk.Text(self.top_level)
        self.txt.pack()

        self.progress_bar = ttk.Progressbar(self.top_level, orient="horizontal", length=200, mode='indeterminate')
        self.progress_bar.pack()
        self.progress_bar.start()

        self.exit_button = tk.Button(self.top_level, text="OK",  command=self.on_exit, state=tk.DISABLED)
        self.exit_button.pack()

    def set_exit_btn_ok(self):
        self.progress_bar.stop()
        self.exit_button.config(state="normal")

    def on_exit(self):
        self.top_level.destroy()