#include "HX711.h"

// 1. CONFIGURAR OS PINOS
HX711 balanca;
int pinoDT = 2;   // DT ou DOUT
int pinoSCK = 3;  // SCK

// 2. VARIÁVEL IMPORTANTE
float fator_calibracao;  // Você vai descobrir este número!

void setup() {
  Serial.begin(9600);
  
  // Iniciar a balança
  balanca.begin(pinoDT, pinoSCK);
  
  Serial.println("=== CALIBRAÇÃO SIMPLES ===");
  Serial.println();
  
  calibrar();  // Chama a função de calibração
}

void loop() {
  // Seu código normal aqui
  float peso = balanca.get_units(5);  // Lê peso com 5 amostras
  Serial.print("Peso: ");
  Serial.print(peso, 1);
  Serial.println(" g");
  
  delay(1000);
}

// 3. FUNÇÃO DE CALIBRAÇÃO (FAZ APENAS UMA VEZ)
void calibrar() {
  Serial.println("PASSO 1: Zerar a balança");
  Serial.println("Remova TUDO da balança");
  Serial.println("Depois pressione 'z'");
  
  while (Serial.read() != 'z');  // Espera pressionar 'z'
  
  balanca.tare();  // Zera a balança
  Serial.println("Balança zerada!");
  delay(1000);
  
  Serial.println();
  Serial.println("PASSO 2: Coloque um peso CONHECIDO");
  Serial.println("Exemplo: 100g, 500g, 1000g");
  Serial.println("Digite o peso em gramas e pressione ENTER");
  
  // Aguarda digitar o peso
  while (!Serial.available());
  String texto = Serial.readString();
  float peso_conhecido = texto.toFloat();
  
  Serial.print("Você colocou: ");
  Serial.print(peso_conhecido);
  Serial.println(" g");
  
  Serial.println("Aguardando 3 segundos para estabilizar...");
  delay(3000);
  
  // Lê o valor COM peso
  float leitura = balanca.get_units(10);
  
  Serial.print("Leitura do sensor: ");
  Serial.println(leitura, 3);
  
  // Calcula o FATOR DE CALIBRAÇÃO
  fator_calibracao = leitura / peso_conhecido;
  
  Serial.println();
  Serial.println("=== RESULTADO ===");
  Serial.print("FATOR DE CALIBRAÇÃO: ");
  Serial.println(fator_calibracao, 7);
  
  // Aplica o fator
  balanca.set_scale(fator_calibracao);
  
  Serial.println();
  Serial.println("Calibração concluída!");
  Serial.println("ANOTE ESTE NÚMERO: ");
  Serial.println(fator_calibracao, 7);
  Serial.println();
  
  // Testa se está certo
  float peso_testado = balanca.get_units(5);
  Serial.print("Peso medido agora: ");
  Serial.print(peso_testado, 1);
  Serial.println(" g");
  
  if (abs(peso_testado - peso_conhecido) < 2) {
    Serial.println("✅ Calibração OK!");
  } else {
    Serial.println("⚠️ Faça novamente");
  }
}