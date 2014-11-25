/* Copyright (c) 2014 Miguel Lechon */
/* 
This file is part of Cyrano. Cyrano is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or (at your 
option) any later version.

Cyrano is distributed in the hope that it will be useful, but WITHOUT ANY 
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with 
Cyrano. If not, see <http://www.gnu.org/licenses/>.
*/

#include <Arduino.h>
using namespace std;

typedef unsigned char uchar;
typedef unsigned long ulong;

void setup(){
	init();
    Serial.begin(115200);
    pinMode(A0, INPUT);
    while(!Serial);
    analogRead(A0);
    delay(3000); // Wait for the python program to open the port and listen
}

void loop(void){
    int value;
    uchar byte;
    uchar MSB_mask = (uchar) 0b10000000;
    uchar LSB_mask = (uchar) 0b01000000;
    uchar even_mask = (uchar) 0b00100000;

    // The theoretical limiting frequency is that of the serial line. I send two
    // bytes per sample at 115200 bauds = 14400 bytes/sec = 7200 samples/sec
    // In practice, probably for not batching the serial writings, I get around 
    // 5800 samples per second
    int sampling_freq = 5000;
    // The temporal resolution of the arduino timer is good for four microsecs
    ulong period = 1e6/sampling_freq;
    ulong t0, t1;
    int even = 1;

    /*  7       6       5       4       3       2       1       0
     * MSB     LSB     EVEN     <=========== ADC bits ==========>
     * The MSB and LSB are redundant, but I'm trying to prevent errors due to 
     * line noise so leave me alone.
     */

    t0 = micros();
    while(1){
        even = (even+1)%2;

        do{
            t1 = micros();
        }while(t0+period > t1);
        t0 = t0+period;

        value = analogRead(A0);

        byte = (uchar)(value >> 5)|MSB_mask; // MSB
        if(even) byte = byte|even_mask;
        Serial.write(byte);

        byte = (uchar)(value & 0b00011111)|LSB_mask; // LSB
        if(even) byte = byte|even_mask;
        Serial.write(byte);
    }
}
