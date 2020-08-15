import tkinter as tk
from tkinter import filedialog as fd
from pathlib import Path
from synapse_counting.synapse_counter import SynapseCounter


class App(object):

    def __init__(self) -> None:
        self.directory = None

    def main(self):
        window = tk.Tk()
        window.title("Super nice automatic microglomeruli counting")
        window.geometry('2000x2000')
        window.rowconfigure(0, weight=0, minsize=25)
        window.rowconfigure(1, weight=1, minsize=100)

        frm_load = tk.Frame(master=window, width=50, height=20, borderwidth=1)
        btn_load = tk.Button(master=frm_load, command=self.ask_image_dir(),  text='Load files')

        btn_load.pack()
        frm_load.grid(row=0)

        frm_main = tk.Frame(master=window)
        show = tk.Canvas(master=frm_main)
        show.pack(fill=tk.BOTH, expand=True)
        frm_main.grid(row=1, padx=5, pady=5)

        window.mainloop()

    def ask_image_dir(self):
        self.directory = fd.askdirectory()

    @property
    def get_directory(self):
        return self.directory

    def image_show(self):
        pass


if __name__ == '__main__':
    app = App()
    app.main()
