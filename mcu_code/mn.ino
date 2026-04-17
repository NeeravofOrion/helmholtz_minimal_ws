#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MLX90393.h>

Adafruit_MLX90393 sensor = Adafruit_MLX90393();

// ===== LAST FIELD =====
float fx = 0, fy = 0, fz = 0;

// ===== STATIC SERIAL BUFFER =====
const int MAX_LEN = 64;
char buffer[MAX_LEN];
int buf_idx = 0;

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
void process_packet();
void set_axis(int pwm_pin, int dir_pin, float val);

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  Wire.begin();

  pinMode(X_PWM, OUTPUT); pinMode(X_DIR, OUTPUT);
  pinMode(Y_PWM, OUTPUT); pinMode(Y_DIR, OUTPUT);
  pinMode(Z_PWM, OUTPUT); pinMode(Z_DIR, OUTPUT);

  if (!sensor.begin_I2C()) {
    while (1); // Hard lock if sensor fails
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

  // SERIAL INPUT (Zero Allocation)
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n') {
      process_packet();
      buf_idx = 0; 
    } else {
      if (buf_idx < MAX_LEN - 1) {
        buffer[buf_idx++] = c;
      }
    }
  }

  unsigned long now = millis();

  // SENSOR (NON-BLOCKING)
  if (measurement_started && (now - measurement_start_time >= SENSOR_READY_MS)) {
    float bx, by, bz;
    if (sensor.readMeasurement(&bx, &by, &bz)) {
      fx = bx; fy = by; fz = bz;
      
      Serial.print("<TEL,");
      Serial.print(fx, 4); Serial.print(",");
      Serial.print(fy, 4); Serial.print(",");
      Serial.print(fz, 4); Serial.println(">");
    }

    sensor.startSingleMeasurement();
    measurement_start_time = millis();
  }
}

// ===== MOTOR =====
void set_axis(int pwm_pin, int dir_pin, float val) {
  // Explicit polarity routing
  if (val >= 0.0) {
    digitalWrite(dir_pin, HIGH);
  } else {
    digitalWrite(dir_pin, LOW);
  }

  // Explicit magnitude clamping without nested macros
  int duty = (int)abs(val);
  if (duty > 255) {
    duty = 255;
  }

  analogWrite(pwm_pin, duty);
}

// ===== PACKET PARSER =====
void process_packet() {
  if (buf_idx < 5) return;
  if (buffer[0] != '<' || buffer[buf_idx - 1] != '>') return;

  // Null-terminate to allow C-string functions
  buffer[buf_idx - 1] = '\0';
  char* ptr = &buffer[1];

  char* type = strtok(ptr, ",");
  if (type == NULL) return;

  if (strcmp(type, "PWM") == 0) {
    char* x_str = strtok(NULL, ",");
    char* y_str = strtok(NULL, ",");
    char* z_str = strtok(NULL, ",");

    if (x_str && y_str && z_str) {
      float x = atof(x_str);
      float y = atof(y_str);
      float z = atof(z_str);

      set_axis(X_PWM, X_DIR, x);
      set_axis(Y_PWM, Y_DIR, y);
      set_axis(Z_PWM, Z_DIR, z);
    }
  }
}