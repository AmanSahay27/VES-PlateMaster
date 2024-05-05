import tkinter as tk
from tkinter import ttk
import subprocess
import csv

class Application:
    def __init__(self, window):
        self.window = window
        self.window.title("Plate Master")

        self.window.configure(bg="light gray")

        # Dropdown menu options 
        self.options = ["UK", "India"]
        self.selected_option = tk.StringVar()
        self.selected_option.set(self.options[0])  # Default selection 

        # Making the dropdown menu
        self.dropdown = ttk.Combobox(window, textvariable=self.selected_option, values=self.options, state="readonly")
        self.dropdown.grid(row=0, column=3, padx=10, pady=10)

        # Buttons for starting, stopping, and reading CSV data
        self.start_button = ttk.Button(window, text="Start", command=self.start_process)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(window, text="Stop", command=self.stop_process, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.read_csv_button = ttk.Button(window, text="Read CSV", command=self.read_csv)
        self.read_csv_button.grid(row=0, column=2, padx=10, pady=10)

        # Create output label and text boxes
        self.output_label = tk.Label(window)
        self.output_label.grid(row=1, column=0, columnspan=4)

        self.unique_id_text_box = tk.Text(window, height=1, width=40)
        self.unique_id_text_box.grid(row=2, column=0, columnspan=4, padx=10, pady=10)

        # Text box for displaying CSV data
        self.text_box = tk.Text(window, height=20, width=80)
        self.text_box.grid(row=3, column=0, columnspan=4, padx=10, pady=10)

        # Reset button
        self.reset_button = ttk.Button(window, text="Reset", command=self.reset_ui)
        self.reset_button.grid(row=4, column=0, columnspan=4, padx=10, pady=10)

        # Initialize variables for subprocess and running state
        self.running = False
        self.sub_process = None

    def start_process(self):
        # Set the running state and button states
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Which code to run based on the selected option
        if self.selected_option.get() == "UK":
            selected_script = "mainuk.py"
        else:
            selected_script = "mainin.py"

        # Start the selected code as a subprocess
        self.sub_process = subprocess.Popen(["python", selected_script])

    def stop_process(self):
        # Stop the running subprocess
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.sub_process:
            self.sub_process.kill()

    def read_csv(self):
        """
        Read the CSV file based on the selected option ("UK" or "India") and display the contents in the text box.
        """
        # Which CSV file to read based on the selected option
        if self.selected_option.get() == "UK":
            csv_file_path = "output.csv"
        else:
            csv_file_path = "indiaoutput.csv"

        try:
            with open(csv_file_path, mode="r") as file:
                reader = csv.DictReader(file)

                # Initialize dictionaries to store data
                highest_confidence = {}
                unique_car_ids = set()

                # Process each row in the CSV file
                for row in reader:
                    car_id = row.get("car_id")
                    license_plate_number = row.get("license_number")
                    entry_time = row.get("entry_time")
                    confidence_score = float(row.get("license_number_score", 0))

                    # Check if the current car_id has a higher confidence score
                    if car_id in highest_confidence:
                        if confidence_score > highest_confidence[car_id]["license_number_score"]:
                            highest_confidence[car_id] = {
                                "license_plate_number": license_plate_number,
                                "entry_time": entry_time,
                                "license_number_score": confidence_score
                            }
                    else:
                        highest_confidence[car_id] = {
                            "license_plate_number": license_plate_number,
                            "entry_time": entry_time,
                            "license_number_score": confidence_score
                        }

                # Initialize a string to hold CSV data to display
                display_content = ""

                # Sort the dictionary by car_id and format the data for display
                for car_id, data in sorted(highest_confidence.items()):
                    license_plate_number = data["license_plate_number"]
                    entry_time = data["entry_time"]
                    display_content += f"License Plate Number: {license_plate_number}, Entry Time: {entry_time}\n"

                    # Add car_id to the set of unique car IDs
                    unique_car_ids.add(car_id)

                # Clear the text box and display the contents
                self.text_box.delete("1.0", tk.END)
                self.text_box.insert(tk.END, display_content)

                # Display the number of unique car IDs 
                self.unique_id_text_box.delete("1.0", tk.END)
                self.unique_id_text_box.insert(tk.END, f"Number of Unique Car IDs: {len(unique_car_ids)}")

        except FileNotFoundError:
            # Handleing file not found error
            self.text_box.delete("1.0", tk.END)
            self.text_box.insert(tk.END, "File not found.")
            self.unique_id_text_box.delete("1.0", tk.END)
            self.unique_id_text_box.insert(tk.END, "File not found.")

    def reset_ui(self):
        """
        Reset the user interface by clearing text boxes and stopping the running process.
        """
        # Clear the text boxes
        self.text_box.delete("1.0", tk.END)
        self.unique_id_text_box.delete("1.0", tk.END)

        # Stop any running process
        self.stop_process()

        # Reset button states
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = Application(root)
    root.mainloop()

if __name__ == "__main__":
    main()
