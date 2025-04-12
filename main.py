from tkinter import *
from tkinter import messagebox, filedialog, ttk
import tkinter as tk
import threading
import keyboard
from googlesearch import search
import webview
import webbrowser
import os
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import time





url_count = 0

class ProgressPopup:
    def __init__(self, root, max_value):
        self.popup = tk.Toplevel(root)
        self.popup.title("Downloading...")
        self.popup.geometry("600x200")

        self.status_var = tk.StringVar()
        self.status_var.set("Starting download...")

        self.label = tk.Label(self.popup, textvariable=self.status_var, font=("Arial", 14))
        self.label.pack(pady=10)

        self.progress = ttk.Progressbar(self.popup, orient="horizontal", length=300, mode="determinate")
        self.progress["maximum"] = max_value
        self.progress["value"] = 0
        self.progress.pack(pady=10)

    def update_progress(self, current, text):
        self.progress["value"] = current
        if text:
            self.status_var.set(text)
        self.popup.update_idletasks()

    def close(self):
        self.popup.destroy()
        
        
class WebCrawlerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Crawler")

        screen_width = (self.root.winfo_screenwidth() / 3)
        screen_height = (self.root.winfo_screenheight() / 1)
        self.root.geometry(f"{int(screen_width)}x{int(screen_height)}")
        self.root.resizable(False, False)

        self.operator_types = [
            "Intitle:", "Intext:",
            "Filetype:", "Inurl:",
            "Link:", "Site:"
        ]

        # Instance variables for links and element
        self.links = []
        self.element = 0
        self.selectedLink = NONE
        
        self.history = []
        self.history_index = -1

        self.setup_ui()

    def setup_ui(self):
        HeaderLabelVar = StringVar()
        HeaderLabelVar.set("Enter Search Term")
        HeaderLabel = Label(self.root, textvariable=HeaderLabelVar, font=("Arial", 20))
        HeaderLabel.place(relx=0.5, rely=0.1, anchor=CENTER)

        self.selected_operator = StringVar()
        self.selected_operator.set("Intitle:")
        operator_sel = OptionMenu(self.root, self.selected_operator, *self.operator_types)
        operator_sel.place(relx=0.5, rely=0.15, anchor=CENTER)

        self.searchTerm = tk.Text(self.root, height=1, width=30, font=("Arial", 15))
        self.searchTerm.place(relx=0.5, rely=0.21, anchor=CENTER)

        getInput_button = Button(self.root, text="Search", command=self.get_input, font=("Arial", 15), bg="Yellow", fg="Black")
        getInput_button.place(relx=0.5, rely=0.28, anchor=CENTER)

        self.eraseInput_button = Button(self.root, text="Clear", command=self.erase_input, font=("Arial", 15), bg="Red", fg="White", state=DISABLED)
        self.eraseInput_button.place(relx=0.3, rely=0.28, anchor=CENTER)

        self.lookInput_button = Button(self.root, text="Open", command=self.look_input, font=("Arial", 15), bg="Green", fg="White", state=DISABLED)
        self.lookInput_button.place(relx=0.7, rely=0.28, anchor=CENTER)

        self.linkList = Listbox(self.root, height=15, width=45, font=("Arial", 15), selectmode=SINGLE)
        self.linkList.place(relx=0.5, rely=0.41, anchor=N)
        self.linkList.bind("<<ListboxSelect>>", lambda event: self.selectLink(self.linkList.get(self.linkList.curselection())))
        
        self.download_button = Button(root, text="Download", command=lambda: self.download_init(self.selectedLink), font=("Arial", 15), bg="Blue", fg="White", state=DISABLED)
        self.download_button.place(relx=0.5, rely=0.9, anchor=CENTER)
        
        self.element_download_list = list()
        
    def download_init(self, url):
        
        total_files, total_size = self.get_file_metadata(url)
        act_size = self.convert_size(total_size)
        
        download_result = messagebox.askquestion("Download", "Do you want to download the selected link?\nTotal files: " + str(total_files) + 
                               "\nTotal Size: " + str(act_size))
        if download_result == 'yes':
            print("Downloading...")
            print(self.element_download_list)
            savepath = filedialog.askdirectory(title="Select Download Directory")
            if savepath:
                self.download_files(self.element_download_list, savepath)
                messagebox.showinfo("Done", f"All files downloaded to:\n{savepath}")
            else:
                messagebox.showerror("Cancelled", "Download Cancelled.")
        else:
            print("Download Cancelled.")
            return
    
    def convert_size(self, size_bytes):
        for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} PB"
    
    def download_files(self, file_links, savepath):
        count = 0
        popup = ProgressPopup(root, max_value=len(file_links))
        for file_url in file_links:
            count += 1
            print(count)
            print(file_url)    
            filename = file_url.split('/')[-1]
            if not filename or not filename[0].isalnum():
                continue
            print(filename)
            file_path = os.path.join(savepath, filename)
            response = requests.get(file_url, stream=True)
            text = f"Downloading:\n {filename}"
            popup.update_progress(count, text)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
        popup.close()
    
    def get_file_metadata(self, url):
        
        response = requests.get(url)
        
        if response.status_code != 200:
            print("Error Fetching URL")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        total_files = 0
        total_size = 0
        
        for link in soup.find_all('a'):
            href = link.get('href')
            
            if href and href not in ['../', '/']:
                file_url = urljoin(url, href)
                self.element_download_list.append(file_url)
                head = requests.head(file_url)
                size = head.headers.get('Content-Length', '0')
                
                try:
                    size_int = int(size)
                    total_size += size_int
                except:
                    size_int = 0
                
                total_files += 1

        return total_files, total_size                
                    
    def selectLink(self, link):
        print("Selected Link:")
        self.selectedLink = link
        self.lookInput_button.config(state=NORMAL)
        self.download_button.config(state=NORMAL)
        
    def get_input(self):
        print("Got Input:")
        searchcookie = (self.selected_operator.get() + "\"index of\"" +
                        "\"" + self.searchTerm.get("1.0", "end-1c") + "\"")
        print(searchcookie)
        self.search_index(searchcookie)

    def erase_input(self):
        print("Erasing Input...")
        self.searchTerm.delete("1.0", "end")
        self.links.clear()
        self.linkList.delete(0, END)
        self.element = 0
        self.eraseInput_button.config(state=DISABLED)
        self.lookInput_button.config(state=DISABLED)
        self.download_button.config(state=DISABLED)
        print(self.links)
        print(self.element)

    def look_input(self):
        global url
        url = self.selectedLink
        browser = webbrowser.get()
        print(url)
        window = webview.create_window("View Scrape", url, width=800, height=600)
        webview.start(self.change_url(url, window))
        
        ##print("Looking Input...")
        #
    def search_index(self, cookie):
        print("Searching Index...")
        results = search(cookie, num_results=10)
        for link in results:
            self.links.append(link)
            self.linkList.insert(self.element, link)
            self.element += 1
        print(self.links)
        print(self.element)
        self.eraseInput_button.config(state=NORMAL)

    def change_url(self, url, window):
        def listen_for_keys():
            while True:
                time.sleep(0.1)
                try:
                    if keyboard.is_pressed('escape'):
                        curr_url = window.get_current_url()
                        if curr_url != url:
                            window.load_url(url)
                            print("URL reset to original.")
                        else:
                            print("Already on original URL.")
                        while keyboard.is_pressed('escape'):
                            time.sleep(0.1)
                except Exception as e:
                    print(f"[ERROR] Escape listener: {e}")
                    break

        threading.Thread(target=listen_for_keys, daemon=True).start()

if __name__ == "__main__":
    root = Tk()
    app = WebCrawlerApp(root)
    root.mainloop()