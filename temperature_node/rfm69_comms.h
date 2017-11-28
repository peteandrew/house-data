#ifndef RFM69COMMS_H_
#define RFM69COMMS_H_

void rfm69_comms_init(void);
void select(void);
void unselect(void);
unsigned char read_reg(unsigned char addr);
void write_reg(unsigned char addr, unsigned char data);

#endif // RFM69COMMS_H_
