#pragma once
#include <Arduino.h>

struct CloudResult {
  int http = 0;
  long entryId = 0;
  long publicEntryId = 0;
  bool readOk = false;
};

long bacaEntryId(int status, String respons);
CloudResult kirimCloud(float suhu, float kelembapan, bool led,
                      bool modeBacaPublik, const char* writeKey);

struct CloudReport {
  CloudResult result;
  bool modeBacaPublik;
};
bool mulaiCloudWorker(unsigned long interval);
bool antreCloud(float suhu, float kelembapan, bool led,
                bool modeBacaPublik, const char* writeKey);
bool ambilHasilCloud(CloudReport& report);
