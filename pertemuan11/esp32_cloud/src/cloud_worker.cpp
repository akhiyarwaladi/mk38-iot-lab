#include "cloud.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
#include <string.h>

struct CloudJob {
  float suhu, kelembapan;
  bool led, modeBacaPublik;
  char key[64];
};
static QueueHandle_t jobs = nullptr, reports = nullptr;
static unsigned long intervalREST = 20000;

static void worker(void*) {
  CloudJob job;
  for (;;) {
    if (xQueueReceive(jobs, &job, portMAX_DELAY) == pdTRUE) {
      CloudReport report;
      report.modeBacaPublik = job.modeBacaPublik;
      report.result = kirimCloud(job.suhu, job.kelembapan, job.led,
                                job.modeBacaPublik, job.key);
      xQueueOverwrite(reports, &report);
      vTaskDelay(pdMS_TO_TICKS(intervalREST));
    }
  }
}

bool mulaiCloudWorker(unsigned long interval) {
  intervalREST = interval;
  jobs = xQueueCreate(1, sizeof(CloudJob));
  reports = xQueueCreate(1, sizeof(CloudReport));
  if (jobs && reports &&
      xTaskCreatePinnedToCore(worker, "REST", 12288, nullptr, 1,
                             nullptr, 1) == pdPASS) return true;
  if (jobs) vQueueDelete(jobs);
  if (reports) vQueueDelete(reports);
  jobs = reports = nullptr;
  return false;
}

bool antreCloud(float suhu, float kelembapan, bool led,
                bool modeBacaPublik, const char* writeKey) {
  if (!jobs) return false;
  CloudJob job{};
  job.suhu = suhu;
  job.kelembapan = kelembapan;
  job.led = led;
  job.modeBacaPublik = modeBacaPublik;
  strncpy(job.key, writeKey, sizeof(job.key) - 1);
  return xQueueOverwrite(jobs, &job) == pdPASS;
}

bool ambilHasilCloud(CloudReport& report) {
  return reports && xQueueReceive(reports, &report, 0) == pdTRUE;
}
