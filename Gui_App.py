import customtkinter as ctk
import serial
import serial.tools.list_ports
import time
import matplotlib

matplotlib.use('TkAgg')  # Set backend before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading


# --- Main App Class ---
class MonitoringApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("V/I Data Acquisition Unit - v2.0")
        self.geometry("1000x650")  # Made window larger for new elements
        ctk.set_appearance_mode("Dark")

        # --- App state variables ---
        self.arduino = None
        self.is_monitoring = False
        self.voltages_data = []  # Store data here to be accessible by other functions
        self.current_data = []  # Store current data
        self.time_data = []  # Store time data
        self.readings_data = []  # Store reading numbers

        # --- Main Layout ---
        self.grid_columnconfigure(0, weight=1, minsize=240)
        self.grid_columnconfigure(1, weight=4)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)

        # --- Main Title ---
        self.title_frame = ctk.CTkFrame(self, corner_radius=10)
        self.title_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")

        self.main_title = ctk.CTkLabel(
            self.title_frame,
            text="V/I (Voltage/Current) Data Acquisition Unit",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.main_title.pack(pady=20)

        # --- Frames ---
        self.control_frame = ctk.CTkFrame(self, width=200, corner_radius=10)
        self.control_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.graph_frame = ctk.CTkFrame(self, corner_radius=10)
        self.graph_frame.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")

        # --- Widgets ---
        self.setup_controls()
        self.setup_graph_controls()

    def __del__(self):
        """Cleanup when app is destroyed"""
        try:
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'fig'):
                plt.close(self.fig)
        except:
            pass

    def setup_controls(self):
        self.label_title = ctk.CTkLabel(self.control_frame, text="Experiment Setup",
                                        font=ctk.CTkFont(size=16, weight="bold"))
        self.label_title.pack(pady=10, padx=10)

        # COM Port Selection
        # ... (same as before) ...
        self.label_com = ctk.CTkLabel(self.control_frame, text="COM Port:")
        self.label_com.pack(pady=(10, 0))
        available_ports = self.get_available_ports()
        self.com_port_menu = ctk.CTkOptionMenu(self.control_frame, values=available_ports)
        self.com_port_menu.pack()
        self.refresh_button = ctk.CTkButton(self.control_frame, text="Refresh Ports", command=self.update_com_ports)
        self.refresh_button.pack(pady=5)

        # Number of Readings Input
        self.label_readings = ctk.CTkLabel(self.control_frame, text="Number of Readings:")
        self.label_readings.pack(pady=(20, 0))
        self.readings_entry = ctk.CTkEntry(self.control_frame, placeholder_text="e.g., 10")
        self.readings_entry.pack()

        # Stabilization Time Input
        self.label_stabilize = ctk.CTkLabel(self.control_frame, text="Stabilization Time (s):")
        self.label_stabilize.pack(pady=(20, 0))
        self.stabilize_entry = ctk.CTkEntry(self.control_frame, placeholder_text="e.g., 5.0")
        self.stabilize_entry.pack()

        # Start Button
        self.start_button = ctk.CTkButton(self.control_frame, text="Start Experiment",
                                          command=self.start_experiment_thread)
        self.start_button.pack(pady=20)

        # --- NEW: Show Data Button ---
        self.show_data_button = ctk.CTkButton(self.control_frame, text="Show Data Table", command=self.show_data_window,
                                              state="disabled")
        self.show_data_button.pack(pady=10)

        # Status Bar
        self.status_label = ctk.CTkLabel(self.control_frame, text="Status: Idle", text_color="gray")
        self.status_label.pack(side="bottom", fill="x", pady=10, padx=10)

    def setup_graph_controls(self):
        # Graph selection section
        self.graph_title = ctk.CTkLabel(
            self.graph_frame,
            text="Graph Configuration",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.graph_title.pack(pady=(20, 10))

        # Create frame for dropdowns
        self.dropdown_frame = ctk.CTkFrame(self.graph_frame)
        self.dropdown_frame.pack(pady=10, padx=20, fill="x")

        # X-axis selection
        self.x_axis_label = ctk.CTkLabel(self.dropdown_frame, text="X-Axis:", font=ctk.CTkFont(size=14, weight="bold"))
        self.x_axis_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.x_axis_options = ["Reading Number", "Time", "Voltage", "Current"]
        self.x_axis_menu = ctk.CTkOptionMenu(
            self.dropdown_frame,
            values=self.x_axis_options,
            command=self.on_axis_change
        )
        self.x_axis_menu.set("Reading Number")
        self.x_axis_menu.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Y-axis selection
        self.y_axis_label = ctk.CTkLabel(self.dropdown_frame, text="Y-Axis:", font=ctk.CTkFont(size=14, weight="bold"))
        self.y_axis_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")

        self.y_axis_options = ["Voltage", "Current", "Reading Number", "Time"]
        self.y_axis_menu = ctk.CTkOptionMenu(
            self.dropdown_frame,
            values=self.y_axis_options,
            command=self.on_axis_change
        )
        self.y_axis_menu.set("Voltage")
        self.y_axis_menu.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Configure column weights for better layout
        self.dropdown_frame.grid_columnconfigure(1, weight=1)

        # Plot area placeholder
        self.plot_placeholder = ctk.CTkLabel(
            self.graph_frame,
            text="Graph will appear here after experiment\n\nSelect X and Y axis options above\nand run an experiment to see data visualization",
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        self.plot_placeholder.pack(expand=True, fill="both", padx=20, pady=20)

    def on_axis_change(self, value):
        """Callback when axis selection changes"""
        # Update graph immediately if data exists and canvas is available
        if hasattr(self, 'canvas') and hasattr(self, 'ax1') and self.voltages_data:
            try:
                # Schedule plot update in main thread
                self.after(0, self.plot_results)
                print(f"Graph update scheduled: X={self.x_axis_menu.get()}, Y={self.y_axis_menu.get()}")
            except Exception as e:
                print(f"Error scheduling graph update: {e}")
        else:
            print(f"Axis changed but no data to plot yet: X={self.x_axis_menu.get()}, Y={self.y_axis_menu.get()}")

    def start_experiment_thread(self):
        if self.is_monitoring:
            print("Experiment already running, ignoring start request")
            return
        print("Starting new experiment thread")
        experiment_thread = threading.Thread(target=self.run_experiment, daemon=True)
        experiment_thread.start()

    def run_experiment(self):
        self.is_monitoring = True
        self.start_button.configure(state="disabled", text="Running...")
        self.show_data_button.configure(state="disabled")  # Disable during run

        # Clear previous data but keep graph structure
        self.voltages_data = []  # Clear previous data
        self.current_data = []  # Clear previous current data
        self.time_data = []  # Clear previous time data
        self.readings_data = []  # Clear previous readings data

        # Schedule graph area clearing in main thread instead of doing it here
        self.after(0, self.clear_graph_area)

        try:
            port = self.com_port_menu.get()
            readings = int(self.readings_entry.get())
            stabilize_time = float(self.stabilize_entry.get())
            if readings <= 0 or stabilize_time < 0: raise ValueError("Inputs must be positive")

            self.status_label.configure(text="Status: Connecting...", text_color="yellow")
            self.arduino = serial.Serial(port=port, baudrate=9600, timeout=2)
            time.sleep(2)

            # --- BUG FIX: Read and discard any startup messages from Arduino ---
            self.arduino.flushInput()  # Clear the input buffer

            # Read startup messages until we get to the calibration message
            while True:
                line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                print(f"Arduino startup message: '{line}'")
                if "Calibrated Current Sensor Offset:" in line:
                    break
                if not line:  # If we get empty lines, continue
                    continue

            # Don't send readings count - Arduino runs continuously
            # self.arduino.write(f"{readings}\n".encode())  # Commented out

            self.status_label.configure(text=f"Status: Stabilizing for {stabilize_time}s...", text_color="cyan")
            time.sleep(stabilize_time)

            for i in range(readings):
                self.status_label.configure(text=f"Status: Taking reading {i + 1}/{readings}...", text_color="green")

                # Read voltage line
                voltage_line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                print(f"Received voltage line: '{voltage_line}'")

                # Read current line
                current_line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                print(f"Received current line: '{current_line}'")

                # Read separator line
                separator_line = self.arduino.readline().decode('utf-8', errors='ignore').strip()
                print(f"Received separator line: '{separator_line}'")

                # Parse voltage - look for it in any of the three lines
                voltage_value = np.nan
                for line in [voltage_line, current_line, separator_line]:
                    if "Input Voltage:" in line:
                        try:
                            value_str = line.split(':')[1].strip().replace(' V', '')
                            voltage_value = float(value_str)
                            print(f"Parsed voltage: {voltage_value}")
                            break
                        except (ValueError, IndexError):
                            print(f"Failed to parse voltage from: '{line}'")

                # Parse current - look for it in any of the three lines
                current_value = np.nan
                for line in [voltage_line, current_line, separator_line]:
                    if "Current:" in line:
                        try:
                            value_str = line.split(':')[1].strip().replace(' A', '')
                            current_value = float(value_str)
                            print(f"Parsed current: {current_value}")
                            break
                        except (ValueError, IndexError):
                            print(f"Failed to parse current from: '{line}'")

                # Store data - ensure all arrays have same length
                self.voltages_data.append(voltage_value)
                self.current_data.append(current_value)
                self.time_data.append(time.time())
                self.readings_data.append(i + 1)

                # Debug: Print array lengths to ensure they stay synchronized
                print(
                    f"Data lengths - V:{len(self.voltages_data)}, I:{len(self.current_data)}, T:{len(self.time_data)}, R:{len(self.readings_data)}")

            self.arduino.close()
            # Schedule graph creation in main thread
            self.after(0, self.create_graph_display)
            self.after(10, self.plot_results)
            self.status_label.configure(text="Status: Experiment Complete!", text_color="lime")
            self.show_data_button.configure(state="normal")  # Enable button after run

        except (ValueError, TypeError) as e:
            self.status_label.configure(text=f"Error: Invalid input. {e}", text_color="red")
        except serial.SerialException as e:
            self.status_label.configure(text=f"Error: Serial connection failed.", text_color="red")
        except Exception as e:
            self.status_label.configure(text=f"Error: {str(e)}", text_color="red")
        finally:
            self.is_monitoring = False
            self.start_button.configure(state="normal", text="Start Experiment")
            print("Experiment thread completed")

    def clear_graph_area(self):
        """Clear the graph area and show placeholder - MUST be called from main thread"""
        try:
            # Remove existing canvas if it exists
            if hasattr(self, 'canvas'):
                self.canvas.get_tk_widget().destroy()
                del self.canvas

            if hasattr(self, 'fig'):
                plt.close(self.fig)
                del self.fig

            if hasattr(self, 'ax1'):
                del self.ax1

            # Close any remaining matplotlib figures
            plt.close('all')

            # Recreate placeholder
            if not hasattr(self, 'plot_placeholder') or not self.plot_placeholder.winfo_exists():
                self.plot_placeholder = ctk.CTkLabel(
                    self.graph_frame,
                    text="Graph will appear here after experiment\n\nSelect X and Y axis options above\nand run an experiment to see data visualization",
                    font=ctk.CTkFont(size=16),
                    text_color="gray"
                )
                self.plot_placeholder.pack(expand=True, fill="both", padx=20, pady=20)

            print("Graph area cleared successfully")
        except Exception as e:
            print(f"Error clearing graph area: {e}")

    def create_graph_display(self):
        """Create the matplotlib graph after experiment completion"""
        # Remove placeholder if it exists
        if hasattr(self, 'plot_placeholder'):
            self.plot_placeholder.destroy()

        # Remove existing canvas if it exists to prevent overlapping
        if hasattr(self, 'canvas'):
            try:
                self.canvas.get_tk_widget().destroy()
            except:
                pass
            del self.canvas

        if hasattr(self, 'fig'):
            try:
                plt.close(self.fig)
            except:
                pass
            del self.fig

        # Close any remaining matplotlib figures
        plt.close('all')

        # Create matplotlib figure and canvas in main thread
        try:
            self.fig, self.ax1 = plt.subplots(figsize=(6, 4), dpi=100)
            self.style_plot()
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
            self.canvas.get_tk_widget().pack(side=ctk.BOTTOM, fill=ctk.BOTH, expand=True, padx=10, pady=10)
            print("Graph display created successfully")
        except Exception as e:
            print(f"Error creating graph display: {e}")
            # Fallback: show error message
            error_label = ctk.CTkLabel(
                self.graph_frame,
                text=f"Error creating graph: {str(e)}",
                font=ctk.CTkFont(size=14),
                text_color="red"
            )
            error_label.pack(expand=True, fill="both", padx=20, pady=20)

    def plot_results(self):
        """Plot results based on selected axes"""
        if not hasattr(self, 'ax1'):
            return

        self.ax1.clear()

        # Get selected axes
        x_axis = self.x_axis_menu.get()
        y_axis = self.y_axis_menu.get()

        # Get data based on selection
        x_data = self.get_data_for_axis(x_axis)
        y_data = self.get_data_for_axis(y_axis)

        # Check if we have data
        if not x_data or not y_data or len(x_data) == 0 or len(y_data) == 0:
            self.ax1.set_title("Experiment Results (No data available)", color="red")
            self.ax1.set_xlabel(self.get_axis_label(x_axis))
            self.ax1.set_ylabel(self.get_axis_label(y_axis))
            self.canvas.draw()
            return

        # Ensure both arrays are same length
        min_length = min(len(x_data), len(y_data))
        x_data = x_data[:min_length]
        y_data = y_data[:min_length]

        # Filter out NaN values but keep indices aligned
        valid_x = []
        valid_y = []
        for i in range(len(x_data)):
            if not (np.isnan(x_data[i]) or np.isnan(y_data[i])):
                valid_x.append(x_data[i])
                valid_y.append(y_data[i])

        if not valid_x:
            self.ax1.set_title("Experiment Results (No valid data received)", color="red")
            self.ax1.set_xlabel(self.get_axis_label(x_axis))
            self.ax1.set_ylabel(self.get_axis_label(y_axis))
            self.canvas.draw()
            return

        # Plot with connected line and markers
        self.ax1.plot(valid_x, valid_y, color='cyan', linestyle='-', linewidth=2,
                      marker='o', markersize=6, markerfacecolor='white',
                      markeredgecolor='cyan', markeredgewidth=2)

        # Set labels and title
        self.ax1.set_xlabel(self.get_axis_label(x_axis))
        self.ax1.set_ylabel(self.get_axis_label(y_axis))
        self.ax1.set_title(f"{y_axis} vs {x_axis}")
        self.ax1.grid(True, which='both', linestyle='--', color='gray', alpha=0.5)

        # Auto-scale the axes for better visualization
        if valid_x and valid_y:
            x_margin = (max(valid_x) - min(valid_x)) * 0.05 if max(valid_x) != min(valid_x) else 0.1
            y_margin = (max(valid_y) - min(valid_y)) * 0.05 if max(valid_y) != min(valid_y) else 0.1
            self.ax1.set_xlim(min(valid_x) - x_margin, max(valid_x) + x_margin)
            self.ax1.set_ylim(min(valid_y) - y_margin, max(valid_y) + y_margin)

        # Force canvas update
        self.canvas.draw()
        self.canvas.flush_events()
        self.update_idletasks()

    def get_data_for_axis(self, axis_name):
        """Return data array for the specified axis"""
        if axis_name == "Voltage":
            return self.voltages_data.copy()
        elif axis_name == "Current":
            return self.current_data.copy()
        elif axis_name == "Time":
            # Convert to relative time (seconds from start)
            if self.time_data and len(self.time_data) > 0:
                start_time = self.time_data[0]
                return [(t - start_time) for t in self.time_data]
            return []
        elif axis_name == "Reading Number":
            return self.readings_data.copy()
        return []

    def get_axis_label(self, axis_name):
        """Return proper label for axis"""
        labels = {
            "Voltage": "Voltage (V)",
            "Current": "Current (A)",
            "Time": "Time (s)",
            "Reading Number": "Reading Number"
        }
        return labels.get(axis_name, axis_name)

    # --- NEW FEATURE: Function to show data in a new window ---
    def show_data_window(self):
        if not self.voltages_data: return

        # Create a new "Toplevel" window
        data_window = ctk.CTkToplevel(self)
        data_window.title("Collected Data")
        data_window.geometry("500x400")

        # Create a textbox to display the data
        textbox = ctk.CTkTextbox(data_window, width=500, height=400, font=("Courier", 12))
        textbox.pack(expand=True, fill="both")

        # Format and insert the data
        header = "Reading | Voltage (V) | Current (A) | Time (s)\n"
        header += "--------|-------------|-------------|----------\n"
        textbox.insert("0.0", header)

        start_time = self.time_data[0] if self.time_data else 0
        for i in range(len(self.voltages_data)):
            voltage = self.voltages_data[i] if i < len(self.voltages_data) else 0
            current = self.current_data[i] if i < len(self.current_data) else 0
            time_val = (self.time_data[i] - start_time) if i < len(self.time_data) else 0
            line = f"{i + 1:<8}| {voltage:<11.4f} | {current:<11.4f} | {time_val:<8.2f}\n"
            textbox.insert(ctk.END, line)

        textbox.configure(state="disabled")  # Make it read-only

    # --- Helper Functions (same as before) ---
    def get_available_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports] if ports else ["No ports found"]

    def update_com_ports(self):
        available_ports = self.get_available_ports()
        self.com_port_menu.configure(values=available_ports)
        if available_ports: self.com_port_menu.set(available_ports[0])

    def style_plot(self):
        self.fig.patch.set_facecolor('#2B2B2B')
        self.ax1.set_facecolor('#2B2B2B')
        self.ax1.tick_params(axis='x', colors='white')
        self.ax1.tick_params(axis='y', colors='cyan')
        self.ax1.spines['left'].set_color('cyan')
        self.ax1.spines['right'].set_color('gray')
        self.ax1.spines['top'].set_color('gray')
        self.ax1.spines['bottom'].set_color('white')
        self.ax1.title.set_color('white')
        self.ax1.xaxis.label.set_color('white')
        self.ax1.yaxis.label.set_color('cyan')


# --- Main entry point ---
if __name__ == "__main__":
    app = MonitoringApp()
    app.mainloop()
