/* 
 * File:   uart.h
 * Author: chavdar
 *
 * Created on February 15, 2017, 1:51 PM
 */

#ifndef UART_H
#define	UART_H

#ifdef	__cplusplus
extern "C" {
#endif

#include <stdio.h>
#include <stdlib.h>
#include <htc.h>
#include <xc.h>

#define BAUD_REG64 (_XTAL_FREQ - BAUD * 64) / (BAUD * 64)
#define BAUD_REG16 (_XTAL_FREQ - BAUD * 16) / (BAUD * 16)

void uart_init(long int baud, long int freq);
void uart_write(char data);   
char uart_read(void);
void uart_read_text(char* data);
void uart_write_text(char* data);
void uart_write_int(int num);
void uart_write_double(double num);
void uart_write_nl();


#ifdef	__cplusplus
}
#endif

#endif	/* UART_H */

