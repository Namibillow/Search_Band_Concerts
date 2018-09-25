# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import datetime
import DB_manager as database


class Window(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.pack()

        # reference to the master widget, which is the tk window
        self.master = master
        self.locations = ['全て', '関東', '近畿', '中部', '九州', '東北', '中国', '北海道', '四国', '沖縄']
        self.now = datetime.datetime.now()
        # create widgets
        self.init_UI()

    def init_UI(self):
        '''
        - Initializes all the widgets needed
        '''
        self.db = database.DataBase()
        # Create frames
        self.main_frame = tk.Frame(self, padx=2, pady=12)
        self.results = tk.Frame(self.main_frame)

        self.tree = ttk.Treeview(self.results, columns=(1, 2, 3, 4, 5, 6), show="headings")
        self.tree.pack(fill="both", expand=True, side='left')
        self.tree.heading(1, text="年")
        self.tree.heading(2, text="月")
        self.tree.heading(3, text="日")
        self.tree.heading(4, text="バンド名")
        self.tree.heading(5, text="地域")
        self.tree.heading(6, text="会場")

        self.tree.column(1, width=30)
        self.tree.column(2, width=30)
        self.tree.column(3, width=30)
        self.tree.column(1, width=70)
        self.tree.column(2, width=40)
        self.tree.column(3, width=50)

        scroll = ttk.Scrollbar(self.results, orient="vertical", command=self.tree.yview)
        scroll.pack(side='right', fill='y')

        self.tree.configure(yscrollcommand=scroll.set)

        #### Top of the main_frame####
        # Create a frame that contains Entry widgets
        self.inputFrame = tk.Frame(self.main_frame, width=500, height=400)
        # Year :  textfield
        self.yearlbl = tk.Label(self.inputFrame, text="年（西暦）：")
        self.year = tk.Entry(self.inputFrame, width=10)
        self.year.insert(0, self.now.year)  # Place holder
        # self.year.bind("<FocusIn>", lambda args: self.year.delete(0, 'end'))

        # Month : textfield
        self.monthlbl = tk.Label(self.inputFrame, text="月 :")
        self.month = tk.Entry(self.inputFrame, width=10)
        self.month.insert(0, "半年先まで可能")
        self.month.bind("<FocusIn>", lambda args: self.month.delete(0, "end"))

        # Band name :  text field
        self.bandslbl = tk.Label(self.inputFrame, text="バンド名：")
        self.commentlbl = tk.Label(self.inputFrame, text="※カンマ「,」区切りで複数入力可能")
        self.bands = ScrolledText(self.inputFrame, wrap=tk.WORD, width=40, height=5, borderwidth=2, relief="groove")

        self.yearlbl.grid(column=0, row=0, sticky="nw", pady=10)
        self.year.grid(column=0, row=0, sticky="nw", padx=100, pady=10)

        self.monthlbl.grid(column=0, row=2, sticky="nw", pady=10)
        self.month.grid(column=0, row=2, sticky="nw", padx=100, pady=10)

        self.bandslbl.grid(column=0, row=4, sticky="nw", pady=10)
        self.commentlbl.grid(column=0, row=4, sticky="nw", padx=100, pady=10)
        self.bands.grid(column=0, row=6, sticky="nw", pady=10)

        # Areas : 10 radio buttons required
        self.area = tk.StringVar()
        self.area.set(self.locations[0])  # Default area is "全て"

        self.arealbl = tk.Label(self.main_frame, text="地域：")
        # Create a frame for area
        self.rbframe = tk.Frame(self.main_frame, width=400, height=200)

        c = 0
        r = 0
        for l in self.locations:
            rb = tk.Radiobutton(self.rbframe, text=l, variable=self.area, value=l)

            if c < 4:
                rb.grid(column=c, row=r, padx=4, pady=2)
                c += 1
            elif c == 4:
                c = 0
                r += 1
                rb.grid(column=c, row=r, padx=4, pady=2)

        ### Bottom of the main_frame ###
        # create a frame contains only buttons
        self.bframe = tk.Frame(self.main_frame)
        self.search = tk.Button(self.bframe, text="検索", command=lambda: self.retrieve_inputs()).pack(side='left', padx=15, pady=10)
        self.reset = tk.Button(self.bframe, text="リセット", command=lambda: self.clear_inputs()).pack(side='right', padx=30)

        ### Use grid to assemble all the frames ###
        self.main_frame.grid(column=0, row=0, sticky="nsew")
        self.results.grid(column=0, row=0, columnspan=1, rowspan=10, sticky="nsew")

        self.inputFrame.grid(column=6, row=0, sticky="w")

        self.arealbl.grid(column=6, row=0, sticky="w", pady=(260, 0))

        self.rbframe.grid(column=6, row=0, columnspan=2, sticky="w", pady=(380, 0))
        # Button at the bottom
        self.bframe.grid(column=6, row=1, columnspan=2, sticky="e")

        # make row 0 resize with the window

        self.main_frame.columnconfigure(0, weight=1)

        self.main_frame.rowconfigure(0, weight=1)

    def retrieve_inputs(self):
        '''
        Called when Search is pushed
        '''
        # Clear the previous data
        self.clear_table()

        bands = self.bands.get("1.0", "end-1c")
        print("Bands: ", bands)

        year = self.year.get()
        print("year: ", year)

        month = self.month.get()
        print("month: ", month)

        area = self.area.get()
        print("area: ", area)

        self.check_input(bands, year, month, area)

    def clear_inputs(self):
        '''
        Reset all the text fields
        '''
        self.year.delete(0, 'end')
        self.month.delete(0, 'end')
        self.bands.delete(1.0, 'end')
        self.area.set(self.locations[0])
        self.clear_table()

    def clear_table(self):
        self.tree.delete(*self.tree.get_children())

    def check_input(self, band, year, month, area):
        '''
        Checks the validity of inputs and pass info to database
        '''
        datas = ""
        if (year.isdigit() and month.isdigit()):
            if datetime.datetime.now().year > int(year) or int(month) < 1 or int(month) > 12:
                datas = self.db.GetTableData()
            else:
                if not band:
                    pass
                    datas = self.db.GetTableData(int(year), int(month), area)
                else:
                    band = [b.strip() for b in band.split(',')]
                    datas = self.db.GetTableData(int(year), int(month), area, band)
        else:
            # messagebox.showinfo("Invalid", "年、月には　英数字だけを入力してください")
            datas = self.db.GetTableData()

        # print(datas)
        for val in datas:
            self.tree.insert('', 'end', values=(val[0], val[1], val[2], val[3], val[4], val[5]))


def run_gui():

    # Creates a blank window
    root = tk.Tk()
    # title of the window
    root.title("Search when your favorite band's concert is")

    app = Window(root)

    root.mainloop()


if __name__ == "__main__":
    run_gui()
