import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import subprocess
import datetime
import csv

class Application:
    def __init__(self, window):
        self.window = window
        self.window.title("License Plate Recognition System")

        # Set the background color of the main window
        self.window.configure(bg="light gray")

        self.start_button = ttk.Button(window, text="Start", command=self.start_process)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(window, text="Stop", command=self.stop_process, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.read_csv_button = ttk.Button(window, text="Read CSV", command=self.read_csv)
        self.read_csv_button.grid(row=0, column=2, padx=10, pady=10)

        self.output_label = tk.Label(window)
        self.output_label.grid(row=1, column=0, columnspan=3)

        # Create a text box to display the number of unique car IDs
        self.unique_id_text_box = tk.Text(window, height=1, width=40)  # Single line for count display
        self.unique_id_text_box.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

        # Create a larger text box by adjusting height and width
        self.text_box = tk.Text(window, height=20, width=80)  # Increase height and width
        self.text_box.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Add a reset button at the bottom of the UI
        self.reset_button = ttk.Button(window, text="Reset", command=self.reset_ui)
        self.reset_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.cap = cv2.VideoCapture(0)
        self.running = False
        self.sub_process = None

    def start_process(self):
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.sub_process = subprocess.Popen(["python", "main91.py"])
        # Call show_frame() if you want to display video frames
        # self.show_frame()

    def stop_process(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.sub_process:
            self.sub_process.kill()

    def read_csv(self):
        """
        Read the specific columns (car_id, license_plate_number, entry_time, and confidence_score) from the readout.csv file.
        Display the information and count of unique car IDs.
        """
        try:
            with open("output.csv", mode="r") as file:
                reader = csv.DictReader(file)
                
                # Initialize a dictionary to store the highest confidence score and corresponding row for each car_id
                highest_confidence = {}
                
                # Initialize a set to hold unique car IDs
                unique_car_ids = set()
                
                # Loop through each row in the CSV file
                for row in reader:
                    # Get the relevant columns from the row
                    car_id = row.get("car_id")
                    license_plate_number = row.get("license_number")
                    entry_time = row.get("entry_time")
                    confidence_score = float(row.get("license_number_score", 0))  # Convert confidence score to float
                    
                    # Check if this car_id has already been encountered
                    if car_id in highest_confidence:
                        # Compare the current confidence score with the highest confidence score for this car_id
                        if confidence_score > highest_confidence[car_id]["license_number_score"]:
                            # Update the entry for this car_id with the current row if the confidence score is higher
                            highest_confidence[car_id] = {
                                "license_plate_number": license_plate_number,
                                "entry_time": entry_time,
                                "license_number_score": confidence_score
                            }
                    else:
                        # Initialize an entry for this car_id with the current row if it's the first occurrence
                        highest_confidence[car_id] = {
                            "license_plate_number": license_plate_number,
                            "entry_time": entry_time,
                            "license_number_score": confidence_score
                        }
                
                # Sort the highest_confidence dictionary by car_id (key)
                sorted_highest_confidence = sorted(highest_confidence.items())
                
                # Initialize an empty string to hold the CSV data to display
                display_content = ""
                
                # Loop through the sorted list and append the data to display_content
                for car_id, data in sorted_highest_confidence:
                    license_plate_number = data["license_plate_number"]
                    entry_time = data["entry_time"]
                    
                    # Add the car_id to the set of unique car IDs
                    unique_car_ids.add(car_id)
                    
                    # Append the data to the display_content string, ensuring one row per line
                    display_content += f"Car ID: {car_id}, License Plate Number: {license_plate_number}, Entry Time: {entry_time}\n"
                
                # Clear the text box and display the content
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, display_content)
                
                # Display the number of unique car IDs in the new text box
                self.unique_id_text_box.delete("1.0", tk.END)
                self.unique_id_text_box.insert(tk.END, f"Number of Unique Car IDs: {len(unique_car_ids)}")
            
        except FileNotFoundError:
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, "File not found.")
            self.unique_id_text_box.delete("1.0", tk.END)
            self.unique_id_text_box.insert(tk.END, "File not found.")


    def reset_ui(self):
        """
        Reset the entire user interface.
        Clear text boxes, stop the running process, and reset the state.
        """
        # Clear the text boxes
        self.text_box.delete("1.0", tk.END)
        self.unique_id_text_box.delete("1.0", tk.END)

        # Stop any running process
        self.stop_process()

        # Reset buttons' states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        # Optionally, restart any other components if necessary

    # This function has been commented out. Uncomment it to display video frames.
    """
    def show_frame(self):
        ret, frame = self.cap.read()
        if ret and self running:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = Image.fromarray(frame)
            frame = ImageTk.PhotoImage(frame)
            self.output_label.configure(image=frame)
            self.output_label.image = frame
            
            # Update text box with detected license plate
            license_plate = detect_license_plate(frame)  # Replace this with your license plate detection logic
            if license_plate:
                self.text_box.delete('1.0', tk.END)  # Clear previous content
                self.text_box.insert(tk.END, f"Detected License Plate: {license_plate}\n")
            
            self.window.after(10, self.show_frame)
        else:
            self.cap.release()
    """

def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()

if __name__ == "__main__":
    main()
