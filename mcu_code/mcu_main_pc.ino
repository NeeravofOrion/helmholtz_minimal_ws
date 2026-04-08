#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MLX90393.h>

Adafruit_MLX90393 sensor = Adafruit_MLX90393();

// ===== LAST FIELD =====
float fx = 0, fy = 0, fz = 0;

// ===== SERIAL =====
String buffer = "";

// ===== MOTOR PINS =====
#define X_PWM 5
#define X_DIR 4
#define Y_PWM 6
#define Y_DIR 7
#define Z_PWM 9
#define Z_DIR 8

// ===== NON-BLOCKING SENSOR =====
bool measurement_started = false;
unsigned long measurement_start_time = 0;
#define SENSOR_READY_MS 15

// ===== DECL =====
void process_line(String line);
void set_axis(int pwm_pin, int dir_pin, float val);
void send_packet(String type, float x, float y, float z);

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Wire.begin();

  pinMode(X_PWM, OUTPUT); pinMode(X_DIR, OUTPUT);
  pinMode(Y_PWM, OUTPUT); pinMode(Y_DIR, OUTPUT);
  pinMode(Z_PWM, OUTPUT); pinMode(Z_DIR, OUTPUT);

  if (!sensor.begin_I2C()) {
    while (1);
  }

  sensor.setGain(MLX90393_GAIN_1X);
  sensor.setResolution(MLX90393_X, MLX90393_RES_16);
  sensor.setResolution(MLX90393_Y, MLX90393_RES_16);
  sensor.setResolution(MLX90393_Z, MLX90393_RES_16);

  sensor.startSingleMeasurement();
  measurement_started = true;
  measurement_start_time = millis();
}

// ===== LOOP =====
void loop() {

  // SERIAL INPUT
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      process_line(buffer);
      buffer = "";
    } else {
      buffer += c;
      if (buffer.length() > 100) buffer = "";
    }
  }

  unsigned long now = millis();

  // SENSOR (NON-BLOCKING)
  if (measurement_started && (now - measurement_start_time >= SENSOR_READY_MS)) {
    float bx, by, bz;
    if (sensor.readMeasurement(&bx, &by, &bz)) {
      fx = bx; fy = by; fz = bz;
      send_packet("TEL", fx, fy, fz);
    }

    sensor.startSingleMeasurement();
    measurement_start_time = millis();
  }
}

// ===== PACKET =====
void process_line(String line) {
  line.trim();
  if (!line.startsWith("<") || !line.endsWith(">")) return;

  line = line.substring(1, line.length() - 1);

  int c1 = line.indexOf(',');
  int c2 = line.indexOf(',', c1 + 1);
  int c3 = line.indexOf(',', c2 + 1);
  if (c1 == -1 || c2 == -1 || c3 == -1) return;

  String type = line.substring(0, c1);
  float x = line.substring(c1 + 1, c2).toFloat();
  float y = line.substring(c2 + 1, c3).toFloat();
  float z = line.substring(c3 + 1).toFloat();

  if (type == "PWM") {
    set_axis(X_PWM, X_DIR, x);
    set_axis(Y_PWM, Y_DIR, y);
    set_axis(Z_PWM, Z_DIR, z);
  }
}

// ===== MOTOR =====
void set_axis(int pwm_pin, int dir_pin, float val) {
  int duty = constrain(abs(val), 0, 255);
  digitalWrite(dir_pin, val >= 0 ? HIGH : LOW);
  analogWrite(pwm_pin, duty);
}

// ===== SERIAL OUT =====
void send_packet(String type, float x, float y, float z) {
  Serial.print('<');
  Serial.print(type);
  Serial.print(',');
  Serial.print(x, 4);
  Serial.print(',');
  Serial.print(y, 4);
  Serial.print(',');
  Serial.print(z, 4);
  Serial.println('>');
}