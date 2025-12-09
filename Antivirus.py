import os, hashlib, sqlite3, shutil, threading, time, tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ------------------------------
# Database Setup
# ------------------------------
def init_db():
    conn = sqlite3.connect("kantivirus.db")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS signatures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hash TEXT UNIQUE NOT NULL
    )""")
    for h in ["5d41402abc4b2a76b9719d911017c592",
              "098f6bcd4621d373cade4e832627b4f6",
              "9e107d9d372bb6826bd81d3542a419d6"]:
        try: cur.execute("INSERT INTO signatures (hash) VALUES (?)",(h,))
        except sqlite3.IntegrityError: pass
    conn.commit(); conn.close()

# ------------------------------
# Core Functions
# ------------------------------
def hash_file(path):
    h=hashlib.md5()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(4096),b''): h.update(chunk)
    return h.hexdigest()

def in_db(h):
    c=sqlite3.connect("kantivirus.db").cursor()
    c.execute("SELECT 1 FROM signatures WHERE hash=?",(h,))
    r=c.fetchone(); c.connection.close(); return r

def quarantine(fp):
    qd="KAV_Quarantine"; os.makedirs(qd,exist_ok=True)
    shutil.move(fp,os.path.join(qd,os.path.basename(fp)))

# ------------------------------
# GUI
# ------------------------------
class KAntiVirusPro:
    def __init__(self,root):
        self.root=root; self.root.title("🛡️ K Anti Virus Pro")
        self.root.geometry("900x560"); self.root.resizable(False,False)
        self.root.configure(bg="#101820")

        self.sidebar=tk.Frame(root,bg="#142233",width=180)
        self.sidebar.pack(side="left",fill="y")

        title=tk.Label(self.sidebar,text="K Anti Virus Pro",bg="#142233",
                       fg="#00FF99",font=("Segoe UI Semibold",14))
        title.pack(pady=20)

        for t in ["Scan","Quarantine","Settings","About"]:
            b=tk.Button(self.sidebar,text=t,width=15,height=2,bg="#1C2A3E",
                        fg="white",relief="flat",activebackground="#00FF99",
                        activeforeground="#000000",font=("Segoe UI",10,"bold"))
            b.pack(pady=5)

        # Main panel
        self.main=tk.Frame(root,bg="#101820"); self.main.pack(expand=True,fill="both")

        self.status_label=tk.Label(self.main,text="System Status: Secure 🟢",
                                   bg="#101820",fg="#00FF99",font=("Segoe UI Semibold",16))
        self.status_label.pack(pady=10)

        # Progress ring (using ttk progressbar)
        style=ttk.Style(); style.theme_use("clam")
        style.configure("green.Horizontal.TProgressbar",
                        troughcolor="#142233",background="#00FF99",bordercolor="#142233")

        self.progress=ttk.Progressbar(self.main,length=500,mode="determinate",
                                      style="green.Horizontal.TProgressbar")
        self.progress.pack(pady=10)

        # Control buttons
        self.btn_browse=tk.Button(self.main,text="📂 Select Folder",command=self.browse,
                                  bg="#00FF99",fg="#000",font=("Segoe UI Semibold",10),width=20)
        self.btn_scan=tk.Button(self.main,text="▶ Start Scan",command=self.scan_thread,
                                bg="#00A3FF",fg="#fff",font=("Segoe UI Semibold",10),width=20)
        self.btn_browse.pack(pady=5); self.btn_scan.pack(pady=5)

        self.output=scrolledtext.ScrolledText(self.main,width=80,height=18,bg="#142233",
                                              fg="#E0E0E0",font=("Consolas",9))
        self.output.pack(padx=15,pady=15)

        self.folder=None

    # --- Browse ---
    def browse(self):
        f=filedialog.askdirectory()
        if f:
            self.folder=f; self.output.insert("end",f"\n📁 Folder selected: {f}\n")
            self.status_label.config(text="Folder selected ✅",fg="#00A3FF")

    # --- Threaded Scan ---
    def scan_thread(self):
        if not self.folder: messagebox.showwarning("Select Folder","Please select a folder to scan."); return
        threading.Thread(target=self.scan,daemon=True).start()

    # --- Scan ---
    def scan(self):
        self.output.insert("end","\n🔍 Scanning started...\n")
        self.status_label.config(text="Scanning...",fg="#00A3FF")
        infected=clean=0; files=list(os.walk(self.folder))
        total=sum(len(f) for _,_,f in files); done=0

        for r,_,fs in files:
            for fn in fs:
                fp=os.path.join(r,fn)
                try:
                    h=hash_file(fp); time.sleep(0.15)
                    if in_db(h):
                        self.output.insert("end",f"⚠️ Threat detected: {fn}\n")
                        quarantine(fp); infected+=1
                    else:
                        self.output.insert("end",f"✅ Clean: {fn}\n")
                        clean+=1
                except Exception as e:
                    self.output.insert("end",f"Error scanning {fn}: {e}\n")
                done+=1; self.progress['value']=done/total*100; self.root.update_idletasks()

        self.status_label.config(
            text=f"Scan Complete 🟢 ({infected} infected, {clean} clean)",
            fg="#00FF99")
        messagebox.showinfo("Scan Complete",
                            f"K Anti Virus Pro Scan finished!\n\nInfected: {infected}\nClean: {clean}")

# ------------------------------
if __name__=="__main__":
    init_db()
    root=tk.Tk()
    app=KAntiVirusPro(root)
    root.mainloop()
