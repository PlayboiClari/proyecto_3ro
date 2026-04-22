
#include <DHT.h>

#define DHT_PIN 2
#define DHT_PIN2 12
#define DHTTYPE DHT22
#define INDUCTIVE_PIN 3
#define SENSOR1 6
#define SENSOR2 7
#define SENSOR3 8
#define LED_R 9 // ERROR!
#define LED_G 10 // ORGANICO
#define LED_B 11 // INORGANICO

unsigned long lastReadTime = 0;
const long interval = 60000;

DHT dht(DHT_PIN, DHTTYPE);
DHT dht2(DHT_PIN2, DHT11);
void setup() {
  Serial.begin(9600);
  dht.begin();
  dht2.begin();
  pinMode(INDUCTIVE_PIN, INPUT);
  pinMode(SENSOR1, INPUT);
  pinMode(SENSOR2, INPUT);
  pinMode(SENSOR3, INPUT);
}

void loop() {
  //Serial.println(digitalRead(SENSOR1));
  if (digitalRead(SENSOR1) == 0) {
    Serial.println("Inductivo");
    int inductivo = digitalRead(INDUCTIVE_PIN);
    if (inductivo) {
    Serial.println("metal");
    onled (LED_B);
    }
    else{
    Serial.println("no metal");
    onled (LED_G);

    }
  }
if (digitalRead(SENSOR2) == 0) {

  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  float humidity2 = dht2.readHumidity();
  float temperature2 = dht2.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Error leyendo DHT22");
    onled(LED_R);
  } 
  else {    

    Serial.println("Leyendo en 1 minuto");

    for (int i = 60; i > 0; i -= 5) {
      Serial.print("Aguarde ");
      Serial.print(i);
      Serial.println(" segundos");
      delay(5000); // espera real de 5 segundos
    }

    Serial.print("Humedad: ");
    Serial.print(humidity);
    Serial.print(" %  |  Temp: ");
    Serial.print(temperature);
    Serial.println(" C");

    Serial.print("Humedad Interna: ");
    Serial.print(humidity2);
    Serial.print(" %  |  Temp Interna: ");
    Serial.print(temperature2);
    Serial.println(" C");

    if (humidity2 - humidity >= 15) {
      Serial.println("Organico"); // comillas dobles
      onled(LED_G);
    }
    Serial.println("Leyendo en 1 minuto");

    for (int i = 60; i > 0; i -= 5) {
      Serial.print("Aguarde ");
      Serial.print(i);
      Serial.println(" segundos");
      delay(5000); // espera real de 5 segundos
    }
    Serial.println("Leyendo en 2 minuto");

    for (int i = 120; i > 0; i -= 10) {
      Serial.print("Aguarde ");
      Serial.print(i);
      Serial.println(" segundos");
      delay(10000); // espera real de 5 segundos
    }
  }
}
if (digitalRead(SENSOR3) == 0) {
  Serial.println('SENSOR3');
  }
delay(500);
}

void onled(int led){
    digitalWrite(led, HIGH);
    delay(500);
    digitalWrite(led, LOW);
    delay(500);
}