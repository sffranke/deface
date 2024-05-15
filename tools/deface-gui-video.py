'''
A GUI to find the values of the rectangle in which no anionymization should take place.
'''
import cv2
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

class VideoPlayer:
    def __init__(self):
        self.cap = None
        self.root = tk.Tk()
        self.root.title("Video Player")
        
        self.max_display_width = 800
        self.max_display_height = 600

        # Create buttons for play, pause, and save coordinates
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(side=tk.TOP)

        self.play_button = ttk.Button(self.button_frame, text="Play", command=self.play_pause_video, state=tk.DISABLED)
        self.play_button.pack(side=tk.LEFT)

        self.save_button = ttk.Button(self.button_frame, text="Save Coordinates", command=self.save_coordinates, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT)

        # Create a slider for video progress
        self.slider = ttk.Scale(self.root, orient=tk.HORIZONTAL, command=self.set_frame, state=tk.DISABLED, length=400)
        self.slider.pack(side=tk.TOP)

        # Create an upload button
        self.upload_button = ttk.Button(self.root, text="Upload Video", command=self.upload_video)
        self.upload_button.pack(side=tk.TOP)

        # Create a canvas to display the video and draw the rectangle overlay
        self.canvas = tk.Canvas(self.root, bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.is_playing = False
        self.rectangle_coords = None
        self.rectangle_id = None

        # Bind mouse events to draw rectangle
        self.canvas.bind("<Button-1>", self.start_rectangle)
        self.canvas.bind("<B1-Motion>", self.update_rectangle)
        self.canvas.bind("<ButtonRelease-1>", self.finish_rectangle)

        self.root.mainloop()

    def unload_video(self):
        self.is_playing = False
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.play_button.config(state=tk.DISABLED)
            self.save_button.config(state=tk.DISABLED)
            self.slider.config(state=tk.DISABLED)

    def play_pause_video(self):
        if self.is_playing:
            self.is_playing = False
            self.play_button.config(text="Play")
        else:
            self.is_playing = True
            self.play_button.config(text="Pause")
            self.update_video()

    def set_frame(self, value):
        try:
            frame_number = int(float(value))
            if self.cap is not None:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                if not self.is_playing:
                    self.update_video()
        except ValueError:
            print("Invalid frame number:", value)

    def update_video(self):
        if self.is_playing and self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                # Get the original dimensions of the frame
                self.original_height, self.original_width, _ = frame.shape

                # Calculate the scaling factor to fit the frame within the defined max width and height
                scale_width = self.max_display_width / self.original_width
                scale_height = self.max_display_height / self.original_height
                self.scale_factor = min(scale_width, scale_height)

                # Calculate the new dimensions
                new_width = int(self.original_width * self.scale_factor)
                new_height = int(self.original_height * self.scale_factor)

                # Resize the frame
                frame = cv2.resize(frame, (new_width, new_height))

                # Convert the frame to RGB format
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Create a PhotoImage object from the frame
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))

                # Display the frame on the canvas
                self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
                self.canvas.image = photo

                # Ensure the canvas matches the size of the displayed frame
                self.canvas.config(width=new_width, height=new_height)

                # Draw rectangle if coordinates are available
                if self.rectangle_coords is not None and self.rectangle_id is None:
                    self.rectangle_id = self.canvas.create_rectangle(self.rectangle_coords, outline="green", width=2)

                # Update the slider position
                self.slider.set(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            else:
                self.is_playing = False
                self.play_button.config(text="Play")

        if self.is_playing:
            self.root.after(20, self.update_video)

    def upload_video(self):
        self.unload_video()
        file_path = filedialog.askopenfilename()
        if file_path:
            self.cap = cv2.VideoCapture(file_path)
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.slider.config(to=frame_count)
            self.play_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            self.slider.config(state=tk.NORMAL)
            self.play_pause_video()
            self.upload_button.pack_forget()

    def save_coordinates(self):
        if self.rectangle_coords is not None:
            # Scale coordinates back to the original size
            scaled_coords = [
                int(self.rectangle_coords[0] / self.scale_factor),
                int(self.rectangle_coords[1] / self.scale_factor),
                int(self.rectangle_coords[2] / self.scale_factor),
                int(self.rectangle_coords[3] / self.scale_factor)
            ]
            print("Rectangle Coordinates (original size):", scaled_coords)

    def start_rectangle(self, event):
        self.rectangle_coords = [event.x, event.y, event.x, event.y]
        if self.rectangle_id is not None:
            self.canvas.delete(self.rectangle_id)
            self.rectangle_id = None

    def update_rectangle(self, event):
        self.rectangle_coords[2] = event.x
        self.rectangle_coords[3] = event.y
        if self.rectangle_id is not None:
            self.canvas.coords(self.rectangle_id, *self.rectangle_coords)
        else:
            self.rectangle_id = self.canvas.create_rectangle(*self.rectangle_coords, outline="green", width=2)

    def finish_rectangle(self, event):
        self.rectangle_coords[2] = event.x
        self.rectangle_coords[3] = event.y
        if self.rectangle_id is not None:
            self.canvas.coords(self.rectangle_id, *self.rectangle_coords)
        else:
            self.rectangle_id = self.canvas.create_rectangle(*self.rectangle_coords, outline="green", width=2)

player = VideoPlayer()

