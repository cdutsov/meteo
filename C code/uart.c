#include "uart.h"
#include "math.h"

#define UART_RX_TRIS TRISC7
#define UART_TX_TRIS TRISC6

void uart_init(long int baud, long int freq) {
	long int spbrg = (freq - baud * 64)/(baud * 64);
	if(spbrg > 255 | spbrg < 10) {
	  spbrg = freq/(baud * 16) - 1; 
	  BRGH = 1; 
	} 
	if(spbrg < 256) {
	  BAUDCONbits.BRG16 = 0;
	  BAUDCONbits.ABDEN = 0;
	  RCSTAbits.SPEN = 1;
	  TXSTAbits.SYNC = 0;
	  RCSTAbits.CREN = 1;
	  TXSTAbits.TXEN = 1;
	  SPBRG = spbrg;
	  PIE1bits.RCIE = 1;
	  UART_RX_TRIS = 1; //Set RX pin as input
	  UART_TX_TRIS = 0;
  }
}

void uart_write(char data) {
	while(!TRMT);
	TXREG = data;
}

void uart_write_text(char* data){
	for(int i = 0; data[i] != '\0'; uart_write(data[i++]));
}

void uart_write_int(int num) {
	char str[10] = {0};
	sprintf(str, "%d", num);
	uart_write_text(str);
}

char uart_read(void){
	while(!RCIF);
	return RCREG;
}

void uart_read_text(char* data){
	int i = 0;
	do {
		data[i++] = uart_read();
	} while (data[i] == '\0');
}

void uart_write_double(double num) {
	char str[10] = {0};
	int int_num = num;
	double part_num = num - int_num;
	int int_part_num = trunc(part_num * 10000);
	sprintf(str, "%d.%04d", int_num, int_part_num);
	uart_write_text(str);
}

void uart_write_nl() {
	uart_write('\n');
}