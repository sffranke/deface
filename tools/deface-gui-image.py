'''
A GUI to find the values of the rectangle in which no anionymization should take place.
'''
import os
import tkinter as tk
import subprocess
from tkinter import filedialog
from PIL import Image, ImageTk

defacepath = "/home/franke/env3_10/bin/deface"

class ImageRectSelector:
    def __init__(self, master):
        self.master = master

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(side=tk.TOP)

        upload_button = tk.Button(self.button_frame, text="Upload Image", command=self.upload_image)
        upload_button.pack(side=tk.LEFT)

        get_coords_button = tk.Button(self.button_frame, text="Get Coordinates", command=self.print_coordinates)
        get_coords_button.pack(side=tk.LEFT)

        self.restart_button = tk.Button(self.button_frame, text="Restart", command=self.restart)
        self.restart_button.pack(side=tk.LEFT)
        self.restart_button.pack_forget()  # Initially hide the button

        self.canvas = tk.Canvas(master, width=800, height=600)
        self.canvas.pack()

        self.rect = None
        self.rect_coords = None
        self.image = None
        self.image_original_size = None

    def upload_image(self):
        file_path = filedialog.askopenfilename()
        self.file = file_path

        if file_path:
            self.image = Image.open(file_path)
            self.image_original_size = self.image.size
            width, height = self.image.size
            aspect_ratio = width / height
            if aspect_ratio > 800 / 600:
                new_width = 800
                new_height = int(800 / aspect_ratio)
            else:
                new_height = 600
                new_width = int(600 * aspect_ratio)
            self.image = self.image.resize((new_width, new_height), Image.ANTIALIAS)
            self.photo = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            new_window_height = new_height + 0
            self.master.geometry(f"800x{new_window_height}")
            self.restart_button.pack()  # Show the restart button

    def print_coordinates(self):
        if self.rect_coords:
            scale_x = self.image_original_size[0] / self.canvas.winfo_width()
            scale_y = self.image_original_size[1] / self.canvas.winfo_height()
            adjusted_coords = (
                int(self.rect_coords[0] * scale_x),
                int(self.rect_coords[1] * scale_y),
                int(self.rect_coords[2] * scale_x),
                int(self.rect_coords[3] * scale_y),
            )
            # Extract filename and extension from the uploaded file path
            filename, ext = os.path.splitext(os.path.basename(self.file))
        
            # Construct the output filename
            output_filename = f"anon_{filename}{ext}" 

            print(defacepath," ",self.file," --boxes --draw-scores --exclude ",adjusted_coords[0]," ",adjusted_coords[1]," ",adjusted_coords[2]," ", adjusted_coords[3]," --boxes --draw-scores --output ", output_filename)
            
            command = [defacepath,self.file, "--boxes","--draw-scores","--exclude",str(adjusted_coords[0]), str(adjusted_coords[1]), str(adjusted_coords[2]),str(adjusted_coords[3]),"--output",output_filename]
            subprocess.run(command)
        else:  
            print("No rectangle drawn yet.")

    def restart(self):
        self.canvas.delete("all")
        self.rect = None
        self.rect_coords = None
        self.image = None
        self.image_original_size = None
        self.restart_button.pack_forget()  # Hide the restart button

    def on_press(self, event):
        if self.rect:
            self.canvas.delete(self.rect)
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_drag(self, event):
        self.curX = self.canvas.canvasx(event.x)
        self.curY = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.curX, self.curY)

    def on_release(self, event):
        self.rect_coords = (self.start_x, self.start_y, self.curX, self.curY)

root = tk.Tk()
app = ImageRectSelector(root)
app.canvas.bind("<ButtonPress-1>", app.on_press)
app.canvas.bind("<B1-Motion>", app.on_drag)
app.canvas.bind("<ButtonRelease-1>", app.on_release)
root.mainloop()
