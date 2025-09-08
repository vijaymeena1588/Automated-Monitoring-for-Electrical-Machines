# Automated-Monitoring-for-Electrical-Machines
Implemented an automated monitoring and data acquisition system for DC/AC electrical machines. Precision sensors were interfaced with microcontrollers to measure voltage, current, and power in real time. A Python-based GUI was designed to visualize and analyze machine performance, enabling advanced control and predictive insights. My role focused on integrating hardware with software, developing the control logic, and ensuring accurate calibration. The outcome was a robust system capable of supporting predictive maintenance and improving machine efficiency.

---

## ⚙️ Key Features

- **Real-Time Data Acquisition:** Precision voltage and current sensors are interfaced with an Arduino microcontroller to capture electrical parameters in real-time. The system calculates and displays power consumption based on these measurements.

- **Hardware-Software Integration:** The core of the project lies in the seamless integration of a physical sensor setup with a robust software interface. My role involved developing the communication protocols and control logic to ensure reliable data flow from the hardware to the software.

- **Automated Calibration:** The current sensor's zero-current offset is automatically calibrated during startup to guarantee the accuracy of all subsequent current measurements.

- **Python-Based GUI:** A custom graphical user interface (GUI) was developed using **CustomTkinter** and **Matplotlib**. This application provides a user-friendly way to:
    - Select COM ports and configure experiment parameters.
    - Visualize real-time and historical data through dynamic, customizable graphs.
    - Display a comprehensive data table of all recorded measurements.
    

- **Predictive Maintenance & Performance Analysis:** By continuously logging and analyzing voltage and current data, the system provides the foundation for **predictive insights**. This allows for the detection of performance degradation and the early identification of potential failures, ultimately improving machine efficiency and reducing downtime.

---

## 🛠️ My Role and Contributions

My focus was on the **hardware-software interface** and **control logic**. I was responsible for:

- **Developing the Arduino Sketch:** I wrote the microcontroller code to accurately read from the voltage and current sensors, perform necessary calculations, and format the data for serial transmission.
- **Designing the Python GUI:** I built the desktop application to handle serial communication, parse incoming data, and present it in a clear, interactive format.
- **Ensuring System Robustness:** I implemented multi-threading to prevent the GUI from freezing during data acquisition and added error handling to manage serial communication failures.
- **Data Handling:** I created the functionality to store, plot, and display the collected data, providing users with a complete view of the experiment's results.
