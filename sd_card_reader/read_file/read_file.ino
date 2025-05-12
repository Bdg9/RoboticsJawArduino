#include <SD.h>
#include <SPI.h>

#define SD_CS BUILTIN_SDCARD  // For Teensy 4.1

File fileList[20]; // Holds up to 20 files
String fileNames[20];
int fileCount = 0;

void listCSVFiles() {
  File root = SD.open("robotics_jaw/");
  //if directory does not exist, print error and return
  if (!root) {
    Serial.println("Failed to open directory.");
    return;
  }
  if (!root.isDirectory()) {
    Serial.println("Not a directory.");
    return;
  }
  Serial.println("Listing CSV files:");
  fileCount = 0;

  while (true) {
    File entry = root.openNextFile();
    //debug print file name
    Serial.print("File: ");
    Serial.println(entry.name());
    if (!entry) break;

    if (!entry.isDirectory() && String(entry.name()).endsWith(".csv")) {
      if (fileCount < 20) {
        fileNames[fileCount] = entry.name();
        fileCount++;
      }
    }
    entry.close();
  }

  Serial.println("Available CSV files:");
  for (int i = 0; i < fileCount; i++) {
    Serial.printf("  [%d] %s\n", i, fileNames[i].c_str());
  }
}

void readCSVFile(const String &filename) {
  // add root directory to filename
  String fullPath = "robotics_jaw/" + filename;
  File dataFile = SD.open(fullPath.c_str());
  if (!dataFile) {
    Serial.println("Failed to open file.");
    return;
  }

  Serial.println("Reading file content:");
  while (dataFile.available()) {
    String line = dataFile.readStringUntil('\n');
    Serial.println(line);
  }
  dataFile.close();
}

void setup() {
  Serial.begin(9600);
  while (!Serial);

  if (!SD.begin(SD_CS)) {
    Serial.println("SD card initialization failed!");
    return;
  }

  Serial.println("SD card initialized.");
  listCSVFiles();
  Serial.println("Enter the number of the file to read:");
}

void loop() {
  if (Serial.available()) {
    int index = Serial.parseInt();
    printf("Selected index: %d\n", index);
    if (index >= 0 && index < fileCount) {
      Serial.printf("Opening file: %s\n", fileNames[index].c_str());
      readCSVFile(fileNames[index]);
    } else {
      Serial.println("Invalid file index. Try again.");
    }

    // Re-list files after reading
    listCSVFiles();
    Serial.println("Enter the number of the file to read:");
  }
}
