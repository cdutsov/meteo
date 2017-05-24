/* 
 * File:   adc.h
 * Author: chavdar
 *
 * Created on February 16, 2017, 11:46 AM
 */

#ifndef ADC_H
#define	ADC_H

#ifdef	__cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include <htc.h>
#include <xc.h>
    
void adc_init();
int adc_read();
void adc_start_conversion(char port);
void adc_ports_init(int tris, int ansel, int ports);
void adc_change_port(char port);


#ifdef	__cplusplus
}
#endif

#endif	/* ADC_H */

