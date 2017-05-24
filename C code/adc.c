#include "adc.h"

void adc_init() {
	ADCON0 &= ~(1 << 7); // 12 bit adc resutl
	ADCON1bits.ADFM = 1;
	ADCON1bits.ADPREF0 = 0;	//vref -> vdd
	ADCON1bits.ADPREF1 = 0;
	ADCON1bits.ADNREF = 0; //vref- -> GND
	ADCON1bits.ADCS = 0b101;	//Fosc/16 -> 4us
	ADCON2 |= 0b00001111;
	ADON = 1;		//turn adc on
	PIE1bits.ADIE = 1;
	ADIF = 0;
}

void adc_ports_init(int tris, int ansel, int ports) {
	tris |= ports;
	ansel |= ports;
}

int adc_read() {
	ADIF = 0;
	return ADRES;
}

void adc_start_conversion(char port){
	if(!ADIF && !ADCON0bits.GO_nDONE) {
		adc_change_port(port);
		ADCON0bits.GO = 1;
	} 
}

void adc_change_port(char port) {
	ADCON0bits.CHS = port;
}