// -------------------------
// Voltage Measurement Setup
// -------------------------
int sensorPin = A2;              // Voltage divider input pin
float voltageRatio = 5.0;        // Voltage divider ratio

// -------------------------
// Current Measurement Setup
// -------------------------
const int analogIn = A4;         // ACS712 output pin
const float mVperAmp = 100.0;    // Sensitivity for ACS712-20A
const int numReadings = 1000;    // Number of samples for averaging
float ACSoffset = 2500.0;        // Zero-current offset (auto-calibrated)

// -------------------------
// Setup
// -------------------------
void setup() {
  Serial.begin(9600);

  // Start messages
  Serial.println("Voltage & Current Measurement");
  Serial.println("-----------------------------------");

  // Auto-calibrate ACS712 offset
  long sum = 0;
  for (int i = 0; i < numReadings; i++) {
    int rawValue = analogRead(analogIn);
    float sensorVoltage = (rawValue * 5000.0) / 1023.0;
    sum += sensorVoltage;
    delay(1);
  }
  ACSoffset = sum / numReadings;  // Save zero-current offset

  Serial.print("Calibrated Current Sensor Offset: ");
  Serial.print(ACSoffset, 2);
  Serial.println(" mV");
  Serial.println();
}

// -------------------------
// Loop
// -------------------------
void loop() {
  // -------------------------
  // Voltage Measurement
  // -------------------------
  int analogValue = analogRead(sensorPin);
  float analogVoltage = (float)analogValue * (4.9 / 1024.0);
  float inputVoltage = analogVoltage * voltageRatio;

  Serial.print("Input Voltage: ");
  Serial.print(inputVoltage-5.0, 2);
  Serial.println(" V");

  delay(1000);  // Small gap before current measurement

  // -------------------------
  // Current Measurement
  // -------------------------
  double sumAmps = 0.0;

  for (int i = 0; i < numReadings; i++) {
    int rawValue = analogRead(analogIn);
    float sensorVoltage = (rawValue * 5000.0) / 1023.0;
    float amps = (sensorVoltage - ACSoffset) / mVperAmp;
    sumAmps += amps;
    delay(1);
  }

  double avgAmps = sumAmps / numReadings;

  Serial.print("Current: ");
  Serial.print(avgAmps, 3);
  Serial.println(" A");

  Serial.println("-----------------------------");
  delay(1000);  // Wait before next cycle
}