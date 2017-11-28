#ifndef TEMP_H
#define TEMP_H

#define THERM_PORT 	PORTD
#define THERM_DDR 	DDRD
#define THERM_PIN 	PIND
#define THERM_DQ 	PD6

#define THERM_INPUT_MODE() 		THERM_DDR&=~(1<<THERM_DQ)
#define THERM_OUTPUT_MODE()		THERM_DDR|=(1<<THERM_DQ)
#define THERM_LOW() 			THERM_PORT&=~(1<<THERM_DQ)
#define THERM_HIGH() 			THERM_PORT|=(1<<THERM_DQ)

#define THERM_CMD_CONVERTTEMP 0x44
#define THERM_CMD_RSCRATCHPAD 0xbe
#define THERM_CMD_WSCRATCHPAD 0x4e
#define THERM_CMD_CPYSCRATCHPAD 0x48
#define THERM_CMD_RECEEPROM 0xb8
#define THERM_CMD_RPWRSUPPLY 0xb4
#define THERM_CMD_SEARCHROM 0xf0
#define THERM_CMD_READROM 0x33
#define THERM_CMD_MATCHROM 0x55
#define THERM_CMD_SKIPROM 0xcc
#define THERM_CMD_ALARMSEARCH 0xec

extern uint8_t therm_reset(void);
extern void therm_write_bit(uint8_t bit);
extern uint8_t therm_read_bit(void);
extern uint8_t therm_read_byte(void);
extern void therm_write_byte(uint8_t byte);

#endif
