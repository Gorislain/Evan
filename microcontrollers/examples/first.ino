#include <WiFi.h>
#include <Firebase_ESP_Client.h>

// Настройка WiFi сети
const char* ssid = "_______";
const char* password = "________";

//учетные данные Firebase проекта
#define API_KEY "________________"
#define DATABASE_URL "https:____________firebasedatabase.app/" 

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

const int gasSensorPin = 34; // Датчик газа MQ-135 подключён к аналоговому пину
const int motionSensorPin = 15; // Датчик движения подключён к цифровому пину
unsigned long sendDataPrevMillis = 0;
bool signupOK = false;
float gasLevel = 0;
bool motionDetected = false;
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 3600;
const int   daylightOffset_sec = 3600;

void setup() {
  Serial.begin(115200);

  // Инициализация пинов датчиков газа и движения
  pinMode(gasSensorPin, INPUT);
  pinMode(motionSensorPin, INPUT);

  // Подключение к WiFi
  WiFi.begin(ssid, password);
  Serial.print("Подключение к Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(300);
  }
  Serial.println("Подключено");

  // Конфигурация Firebase
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;

  // Попытка регистрации (нужно выполнить только один раз)
  if (Firebase.signUp(&config, &auth, "", "")) {
    Serial.println("Регистрация в Firebase прошла успешно");
    signupOK = true;
  } else {
    Serial.printf("Не удалось зарегистрироваться: %s\n", config.signer.signupError.message.c_str());
  }

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  // Синхронизация времени через NTP
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  Serial.println("Ожидание синхронизации времени с NTP");
  while (!time(nullptr)) {
    delay(1000);
    Serial.println("Синхронизация...");
  }
  Serial.println("Время синхронизировано");
}

void loop() {
  if (millis() - sendDataPrevMillis > 10000 || sendDataPrevMillis == 0) { // Отправка данных каждые 10 секунд
    sendDataPrevMillis = millis();

    // Чтение уровня газа и обнаружение движения
    gasLevel = analogRead(gasSensorPin); // Чтение аналогового значения с датчика MQ-135
    motionDetected = digitalRead(motionSensorPin); // Чтение цифрового значения с датчика движения
    Serial.print("Уровень газа: ");
    Serial.println(gasLevel);
    Serial.print("Обнаружено движение: ");
    Serial.println(motionDetected ? "Да" : "Нет");

    // Подготовка строки времени
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
      Serial.println("Не удалось получить время");
      return;
    }
    char timeStr[64];
    strftime(timeStr, sizeof(timeStr), "%Y:%m:%d:%H:%M:%S", &timeinfo);

    // Путь в Firebase для данных уровня газа и движения
    String firebasePathGas = String("sensors/gas/") + timeStr;
    String firebasePathMotion = String("sensors/motion/") + timeStr;

    // Отправка данных уровня газа в Firebase
    if (signupOK && Firebase.RTDB.setFloat(&fbdo, firebasePathGas.c_str(), gasLevel)) {
      Serial.println("Данные уровня газа отправлены в Firebase");
    } else {
      Serial.println("Не удалось отправить данные уровня газа");
      Serial.println(fbdo.errorReason());
    }

    // Отправка данных о движении в Firebase
    if (signupOK && Firebase.RTDB.setBool(&fbdo, firebasePathMotion.c_str(), motionDetected)) {
      Serial.println("Данные о движении отправлены в Firebase");
    } else {
      Serial.println("Не удалось отправить данные о движении");
      Serial.println(fbdo.errorReason());
    }
  }
}
