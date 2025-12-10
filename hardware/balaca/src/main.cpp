#include <Arduino.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "HX711.h"

HX711 scale;
float valor;
float peso;
const float ZERO_SENSOR = -83746.00;    // Valor do sensor com 0g
const float MIL_SENSOR = -539700.50;    // Valor do sensor com 1000g
const float DIFERENCA_SENSOR = ZERO_SENSOR - MIL_SENSOR;  // = 455954.50

// Fator de conversão (1000g / diferença do sensor)
const float FATOR_CONVERSAO = 1000.0 / DIFERENCA_SENSOR;
// Configurações WiFi
const char* WIFI_SSID = "uaifai-tiradentes";
const char* WIFI_PASSWORD = "bemvindoaocesar";
const char* API_BASE_URL = "http://172.26.65.26:5000";

// Hardware
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Variáveis
int cont = 0;
String produto_atual = "";
String produto_chave = "";  // Chave no JSON: "1", "2", "3"
float peso_atual = 0;
float pesoMin = 0;
bool alerta_disp = false;
bool alerta_indisp = false;
const int pinoBotao = 26;
String validade = "";
void setup_wifi() {
  lcd.clear();
  lcd.print("Conectando WiFi");
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  
  // 10 segundos máximo (20 tentativas de 500ms)
  for(int i = 0; i < 20 && WiFi.status() != WL_CONNECTED; i++) {
    delay(500);
  }
  
  if(WiFi.status() == WL_CONNECTED) {
    lcd.clear();
    lcd.print("WiFi Conectado");
    Serial.println("WiFi: OK");
    delay(600);
  } else {
    lcd.clear();
    lcd.print("WiFi Falhou");
    Serial.println("WiFi: ERRO");
    delay(1500);
  }
}
void consultar_produto_ativo() {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/cozinha/ativo");
  http.setTimeout(3000);
  
  if (http.GET() == 200) {
    String response = http.getString();
    StaticJsonDocument<256> doc;
    
    if (!deserializeJson(doc, response)) {
      // Converte para char[] para economizar RAM
      String temp = doc["nome"].as<String>();
      validade = doc["validade"].as<String>();
      produto_atual = temp;
      
      produto_chave = String(doc["id"].as<int>());
      peso_atual = doc["peso"];
      pesoMin = doc["pesoMin"];
      
    }
  }
  
  http.end();
}

bool atualizar_status_produto(String chave, bool disponivel) {
  if (WiFi.status() != WL_CONNECTED) return false;
  
  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/cozinha/" + chave + 
             (disponivel ? "/disponivel" : "/indisponivel"));
  http.addHeader("Content-Type", "application/json");
  
  bool success = (http.POST("{}") == 200);
  http.end();
  
  return success;
}

void atualizar_produto_ativo(String chave) {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/cozinha/" + chave + "/ativo");
  http.addHeader("Content-Type", "application/json");
  http.POST("{}");
  http.end();
}
void setup() {
  Serial.begin(115200);
  
  // LCD
  scale.begin(13,14);
  Wire.begin(21, 22);
  lcd.init();
  lcd.backlight();
  lcd.clear();
  lcd.print("Iniciando...");
  delay(800);


  // Botão
  pinMode(pinoBotao, INPUT_PULLUP);
  
  // WiFi
  setup_wifi();
  
  Serial.println("Sistema OK");
}

void loop() {
  static unsigned long ultima_consulta = 0;
  static unsigned long ultimo_botao = 0;
  
  unsigned long agora = millis();
  valor =  scale.get_units(),1;
  // 1. CONSULTA API (5 segundos)
  if (agora - ultima_consulta >= 5000) {
    consultar_produto_ativo();
    ultima_consulta = agora;
  }
  
  // 2. BOTÃO (com debounce)
  
  int estado = digitalRead(pinoBotao);
  
  if (estado == LOW) {
    Serial.println("BOTAO PRESSIONADO!");
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Validade: ");
    lcd.setCursor(0, 1);
    Serial.print(validade);
    lcd.print(validade);
    while(digitalRead(pinoBotao) == LOW) {
      delay(10);
    }
    
    Serial.println("Botao solto");
    delay(200);
  }
  
 
  
  // 3. DISPLAY
  lcd.clear();
  lcd.setCursor(0, 0);
  
  // Linha 1: Nome do produto
  lcd.print(produto_atual.substring(0, 16)); // Limita a 16 caracteres
  peso = (ZERO_SENSOR - valor) * FATOR_CONVERSAO;
  
  // Linha 2: Peso
  lcd.setCursor(0, 1);
  Serial.println(valor);
  lcd.print(peso, 1);
  lcd.print("g/");
  lcd.print(pesoMin,1);

  
 
    bool abaixo_minimo = (peso <= pesoMin);
    
    if (abaixo_minimo) {
      lcd.print("MIN!");
      
      if (!alerta_indisp) {
        if (atualizar_status_produto(produto_chave, false)) {
          alerta_indisp = true;
          alerta_disp = false;
          lcd.setCursor(15, 0);
          lcd.print("!");
        }
      }
    } else {
      if (!alerta_disp) {
        if (atualizar_status_produto(produto_chave, true)) {
          alerta_indisp = false;
          alerta_disp = true;
          lcd.setCursor(15, 0);
          lcd.print(" ");
        }
      }
    }
    
 
  
  delay(2000);
}