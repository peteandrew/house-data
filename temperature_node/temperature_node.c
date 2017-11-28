#include <util/delay.h>
#include <stdlib.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h> 

#include "temp.h"
#include "spi.h"
#include "rfm69_comms.h"

volatile uint8_t watchdog_counter = 14;

ISR(WDT_OVERFLOW_vect)
{
    sleep_disable();
    watchdog_counter++;
}

int main(void)
{
    rfm69_comms_init();

    // set standby mode
    write_reg(0x01, 0x04);
    _delay_ms(1);

    // config
    const uint8_t CONFIG[][2] =
    {
        { 0x01, 0x04 }, // REG_OPMODE, RF_OPMODE_STANDBY
        { 0x02, 0x00 }, // REG_DATAMODUL, RF_DATAMODUL_DATAMODE_PACKET | RF_DATAMODUL_MODULATIONTYPE_FSK | RF_DATAMODUL_MODULATIONSHAPING_00
        { 0x03, 0x02 }, // REG_BITRATEMSB, RF_BITRATEMSB_55555 - default: 4.8 KBPS
        { 0x04, 0x40 }, // REG_BITRATELSB, RF_BITRATELSB_55555
        { 0x05, 0x03 }, // REG_FDEVMSB, RF_FDEVMSB_50000 - default: 5KHz, (FDEV + BitRate / 2 <= 500KHz)
        { 0x06, 0x33 }, // REG_FDEVLSB, RF_FDEVLSB_50000

        { 0x07, 0x6C }, // REG_FRFMSB, RF_FRFMSB_433
        { 0x08, 0x40 }, // REG_FRFMID, RF_FRFMID_433
        { 0x09, 0x00 }, // REG_FRFLSB, RF_FRFLSB_433

        { 0x11, 0x94 }, // REG_PALEVEL, PA0_ON | power level 20

        { 0x19, 0x42 }, // REG_RXBW

        { 0x28, 0x10 }, // REG_IRQFLAGS2
        { 0x2E, 0x88 }, // REG_SYNCCONFIG, RF_SYNC_ON | RF_SYNC_FIFOFILL_AUTO | RF_SYNC_SIZE_2 | RF_SYNC_TOL_0
        { 0x2F, 0x2D }, // REG_SYNCVALUE1, 0x2D -  attempt to make this compatible with sync1 byte of RFM12B lib
        { 0x30, 100 }, // REG_SYNCVALUE2, networkID - NETWORK ID
        { 0x37, 0x90 }, // REG_PACKETCONFIG1, RF_PACKET1_FORMAT_VARIABLE | RF_PACKET1_DCFREE_OFF | RF_PACKET1_CRC_ON | RF_PACKET1_CRCAUTOCLEAR_ON | RF_PACKET1_ADRSFILTERING_OFF
        { 0x38, 66 }, // REG_PAYLOADLENGTH, 66 - in variable length mode: the max frame size, not used in TX
        { 0x3C, 0x8F }, // REG_FIFOTHRESH, RF_FIFOTHRESH_TXSTART_FIFONOTEMPTY | RF_FIFOTHRESH_VALUE - TX on FIFO not empty
        { 0x3D, 0x12 }, // REG_PACKETCONFIG2, RF_PACKET2_RXRESTARTDELAY_2BITS | RF_PACKET2_AUTORXRESTART_ON | RF_PACKET2_AES_OFF - RXRESTARTDELAY must match transmitter PA ramp-down time (bitrate dependent)

        { 0x93, 0x1A }, // REG_OCP
        {255, 0}
    };

    for (uint8_t i = 0; CONFIG[i][0] != 255; i++) {
        write_reg(CONFIG[i][0], CONFIG[i][1]);
        _delay_ms(1);
    }

    _delay_ms(10);

    select();
    char key[16] = "sampleEncryptKey";
    spi_send_byte(0x3E | 0x80); // Write to REG_AESKEY1
    for (uint8_t i = 0; i < 16; i++)
        spi_send_byte(key[i]);
    unselect();
    _delay_ms(1);
    write_reg(0x3D, 0x13); // REG_PACKETCONFIG2, AES ON

    _delay_ms(10);

    uint8_t scratchpad[2] = {0,0};
    uint8_t error;

    // Set up watchdog
    WDTCSR |= (1 << WDCE | 1 << WDE);
    WDTCSR = (1 << WDIE | 1 << WDP3); // Watchdog prescale for ~4s timeout

    set_sleep_mode(SLEEP_MODE_PWR_DOWN);

    sei();

    while(1) {
        // Count of 14 = ~60s
        if (watchdog_counter > 13) {

            if(therm_reset())
                error = 1;
            else
                error = 0;

            if (!error) {
                therm_write_byte(THERM_CMD_SKIPROM);
                therm_write_byte(THERM_CMD_CONVERTTEMP);
                _delay_ms(800);
                therm_reset();
                therm_write_byte(THERM_CMD_SKIPROM);
                therm_write_byte(THERM_CMD_RSCRATCHPAD);
                scratchpad[0]=therm_read_byte();
                scratchpad[1]=therm_read_byte();
            }

            // write to FIFO
            select();
            spi_send_byte(0x80); // Write to FIFO (0x00)
            spi_send_byte(5); // buffer size + 3
            spi_send_byte(1);
            spi_send_byte(2);
            spi_send_byte(0);
            spi_send_byte(scratchpad[1]);
            spi_send_byte(scratchpad[0]);
            unselect();

            // set transmit mode
            write_reg(0x01, 0x0C);

            // wait for packet to be sent
            while ((read_reg(0x28) & 0x08) == 0x00);

            // set standby mode
            write_reg(0x01, 0x04);

            watchdog_counter = 0;
        }
        
        sleep_enable();
        sleep_cpu();
    }

    return 0;
}
