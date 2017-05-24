/* 
 * File:   test_led.c
 * Author: chavdar
 *
 * Created on February 10, 2017, 10:22 AM
 */

// CONFIG1
#pragma config FOSC = ECH       // Oscillator Selection Bits (ECH, External Clock, High Power Mode (4-20 MHz): device clock supplied to CLKIN pins)
#pragma config WDTE = OFF       // Watchdog Timer Enable (WDT disabled)
#pragma config PWRTE = OFF      // Power-up Timer Enable (PWRT disabled)
#pragma config MCLRE = ON       // MCLR Pin Function Select (MCLR/VPP pin function is MCLR)
#pragma config CP = OFF         // Flash Program Memory Code Protection (Program memory code protection is disabled)
#pragma config BOREN = ON       // Brown-out Reset Enable (Brown-out Reset enabled)
#pragma config CLKOUTEN = OFF   // Clock Out Enable (CLKOUT function is disabled. I/O or oscillator function on the CLKOUT pin)
#pragma config IESO = ON        // Internal/External Switchover Mode (Internal/External Switchover Mode is enabled)
#pragma config FCMEN = ON       // Fail-Safe Clock Monitor Enable (Fail-Safe Clock Monitor is enabled)

// CONFIG2
#pragma config WRT = OFF        // Flash Memory Self-Write Protection (Write protection off)
#pragma config PPS1WAY = ON     // Peripheral Pin Select one-way control (The PPSLOCK bit cannot be cleared once it is set by software)
#pragma config ZCD = OFF        // Zero-cross detect disable (Zero-cross detect circuit is disabled at POR)
#pragma config PLLEN = ON       // Phase Lock Loop enable (4x PLL is always enabled)
#pragma config STVREN = ON      // Stack Overflow/Underflow Reset Enable (Stack Overflow or Underflow will cause a Reset)
#pragma config BORV = LO        //  Brown-out Reset Voltage Selection (Brown-out Reset Voltage (Vbor), low trip point selected.)
#pragma config LPBOR = OFF      // Low-Power Brown Out Reset (Low-Power BOR is disabled)
#pragma config LVP = ON         // Low-Voltage Programming Enable (Low-voltage programming enabled)

// #pragma config statements should precede project file includes.
// Use project enums instead of #define for ON and OFF.

#define _XTAL_FREQ	4000000
#define BAUD		9600

#include <stdio.h>
#include <stdlib.h>
#include <htc.h>
#include <xc.h>
#include "uart.h"
#include "adc.h"

#define HEATER_PIN	1
#define LED_RED		0
#define LEDS_LAT	LATB
#define LEDS_TRIS	TRISB

#define BUTTON_TRIS	4
#define BUTTON_PIN	4

#define OSC_FREQ 0b01101000 //4MHz

int BLINKER = HEATER_PIN;
volatile unsigned int i = 0, j = 0, k = 0, end_k = 0;
volatile unsigned int is_heating = 0;
volatile unsigned int adc_port = 0;

void main()
{
	OSCCON = OSC_FREQ;	//set main osc
	
	OSCCONbits.SCS1 = 1;	//turn main osc on
	LEDS_TRIS &= ~(1 << HEATER_PIN | 1 << LED_RED);
	LEDS_LAT &= ~(1 << HEATER_PIN | 1 << LED_RED);
	
	__delay_us(100);
	ANSELBbits.ANSB4 = 0;	
	ANSELBbits.ANSB5 = 0;	
	ANSELBbits.ANSB6 = 0;	
	ANSELBbits.ANSB7 = 0;	

	LEDS_LAT |= 1 << HEATER_PIN;
	__delay_us(280);
	LEDS_LAT &= ~(1 << HEATER_PIN);
	
	INTCONbits.GIE = 1;
	INTCONbits.PEIE = 1;
//	INTCONbits.IOCIE = 1;
//	IOCBPbits.IOCBP4 = 1;	
	
	uart_init(BAUD, _XTAL_FREQ);
	uart_write_text("starting...\n");
	
	adc_init();
	adc_ports_init(TRISA, ANSELA, 0b0000111); //adc tris, adc ansel and pin number
	
	//TIMER0 setup
	OPTION_REGbits.PS = 1;
	OPTION_REGbits.PS1 = 1;
	OPTION_REGbits.PS2 = 1;
	OPTION_REGbits.PSA = 1;
	INTCONbits.TMR0IE = 1;
	INTCONbits.TMR0IF = 0;
	TMR0 = 244;
	OPTION_REGbits.TMR0CS = 0;
	
	while (1) {		
	}
}

void interrupt ISR() {
//	if(IOCBFbits.IOCBF4) {
//		//LEDS_LAT &= ~(1 << LED_RED | 1 << LED_GREEN);
//		IOCBFbits.IOCBF4 = 0;
//		if(PORTBbits.RB4)
//			BLINKER = LED_RED;
//		else
//			BLINKER = HEATER_PIN;
//	}
	
	//ADC
	if(ADIF & !ADCON0bits.GO_nDONE) {
		double adc_voltage = (double)adc_read()*(double)5/(double)4096;
		LEDS_LAT &= ~(1 << LED_RED);
		switch(adc_port) {
		case 0:
			uart_write_text("dust_particles, ");
			uart_write_double(adc_voltage*11);
			uart_write_text("\n");
			break;
		case 1:
			uart_write_text("carbon_monoxide, ");
			uart_write_double(adc_voltage);
			uart_write_text("\n");
			break;

		}
	}
	
	//UART
	if(RCIF && RCIE) {
		char data = uart_read();
	}
	
	//Catch timer0
	if(TMR0IE && TMR0IF) {
		if(i++ == 255) {
			if(j++ == 10) {
				LEDS_LAT |= 1 << LED_RED;
				__delay_us(280);
				adc_port = 0;
				adc_start_conversion(adc_port);
				j = 0;
				if(k++ == end_k) {
					if(is_heating) {
						adc_port = 1;
						adc_start_conversion(adc_port);
						LEDS_LAT &= ~(1 << HEATER_PIN);
						is_heating = 0;
						end_k = 45;
					} else {
						LEDS_LAT |= 1 << HEATER_PIN;
						is_heating = 1;
						end_k = 60;
					}
					k = 0;
				}
			}
			i = 0;
		}
		TMR0IF = 0;
	}
}