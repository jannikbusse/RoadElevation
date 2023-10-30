/**
 * Road-Generation
 * --------------------------------------------------------
 * Copyright (c) 2021 Institut für Kraftfahrzeuge, RWTH Aachen, ika
 * Report bugs and download new versions https://github.com/ika-rwth-aachen/RoadGeneration
 *
 * This library is distributed under the MIT License.
 */

#ifndef SETTINGS
#define SETTINGS

#include <string.h>
#include <stdio.h>
#include <iostream>
#include <vector>


/**
 * @brief A helper struct that stores the command line arguments for the executable.
 * 
 */
struct settingsExec{
    char* fileName;
    char* outputName;
    bool suppressOutput = false;
    bool overwriteLog = true;

};

#endif