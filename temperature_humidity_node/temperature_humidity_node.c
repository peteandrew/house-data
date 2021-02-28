#include <util/delay.h>
#include <stdlib.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/sleep.h>

#include "spi.h"
#include "rfm69_comms.h"

#define NODE_ID 4
// RHT03
#define NODE_TYPE 'R'

#define LED_PIN PINB0
#define DEBUG_PIN PINB1
#define RHT03_PIN PINA0

// Count of 28 = ~120s
// Count of 14 = ~60s
// Count of 1 = ~4s
#define WATCHDOG_COUNT_WAKEUP 28
volatile uint8_t watchdog_counter = WATCHDOG_COUNT_WAKEUP + 1;

ISR(WDT_vect)
{
    sleep_disable();
    watchdog_counter++;
}

void led_blink(int blinkMS)
{
    PORTB &= ~(1 << LED_PIN);
    for (int i = 0; i < blinkMS; i++) {
        _delay_ms(1);
    }
    PORTB |= (1 << LED_PIN);
}

void debug_out(int8_t value)
{
    if (value) {
        PORTB |= (1 << DEBUG_PIN);
    } else {
        PORTB &= ~(1 << DEBUG_PIN);
    }
}

uint8_t read_bit(void)
{
    // Reset timer
    TCNT0 = 0x00;
    // Wait for pin to go high
    while ((PINA & (1 << RHT03_PIN)) == 0) {
        _delay_us(1);
    }
    // Start timer (/8 prescaler 1MHz)
    TCCR0B |= (1 << CS01);
    // Wait for pin to return low
    while ((PINA & (1 << RHT03_PIN)) != 0) {
        _delay_us(1);
    }
    // Stop timer
    TCCR0B &= ~(1 << CS01);
    if ((uint8_t)TCNT0 > 40) {
        return 1;
    } else {
        return 0;
    }
}

uint8_t valid_checksum(uint8_t bytes[])
{
    uint8_t sum = 0;
    for (uint8_t i = 0; i < 4; i++) {
        sum = sum + bytes[i];
    }
    if (sum == bytes[4]) {
        return 1;
    }
    return 0;
}

int main(void)
{
    DDRB |= (1 << LED_PIN | 1 << DEBUG_PIN);
    PORTB &= ~(1 << LED_PIN | 1 << DEBUG_PIN);

    DDRA &= ~(1 << RHT03_PIN);

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

        //{ 0x11, 0x94 }, // REG_PALEVEL, PA0_ON | power level 20
        { 0x11, 0x9C }, // REG_PALEVEL, PA0_ON | power level 28

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

    // Set up timer
    TCCR0A = 0x00; // Normal mode
    TCCR0B = 0x00; // Stopped

    // Set up watchdog
    WDTCSR |= (1 << WDCE | 1 << WDE);
    WDTCSR = (1 << WDIE | 1 << WDP3); // Watchdog prescale for ~4s timeout

    PORTB |= (1 << LED_PIN);

    set_sleep_mode(SLEEP_MODE_PWR_DOWN);

    sei();

    while(1) {
        if (watchdog_counter > WATCHDOG_COUNT_WAKEUP) {
            led_blink(1000);

            // Pull pin low for 2ms then return high
            DDRA |= (1 << RHT03_PIN);
            PORTA &= ~(1 << RHT03_PIN);
            _delay_ms(2);
            PORTA |= (1 << RHT03_PIN);
            // Set pin to input mode
            DDRA &= ~(1 << RHT03_PIN);
            // Sensor will pull pin low wait a few microseconds before checking value
            _delay_us(30);

            // Sensor sends one pre-amble period
            read_bit();

            uint8_t vals[] = {0, 0, 0, 0, 0};

            // Sensor sends 40 bits (16 humidity, 16 temp, 8 checksum)
            // Bits start with ~50us low period followed by a high period
            // If high period is 26-28us bit is LOW
            // If high period is 70us bit is HIGH
            for (int i = 0; i < 40; i++) {
                uint8_t bit = read_bit();
                int byteNum = i / 8;

                if (bit) {
                    if (byteNum == 0) {
                        vals[0] |= (1 << (7 - i));
                    } else if (byteNum == 1) {
                        vals[1] |= (1 << (15 - i));
                    } else if (byteNum == 2) {
                        vals[2] |= (1 << (23 - i));
                    } else if (byteNum == 3) {
                        vals[3] |= (1 << (31 - i));
                    } else if (byteNum == 4) {
                        vals[4] |= (1 << (39 - i));
                    }
                }
            }

            //if (valid_checksum(vals)) {

                led_blink(100);
                _delay_ms(50);
                led_blink(100);

                // write to FIFO
                select();
                spi_send_byte(0x80); // Write to FIFO (0x00)
                spi_send_byte(8); // frame length
                spi_send_byte(1); // to address ID
                spi_send_byte(NODE_ID); // from address ID
                spi_send_byte(0); // send ack
                spi_send_byte(NODE_TYPE);
                spi_send_byte(vals[0]);
                spi_send_byte(vals[1]);
                spi_send_byte(vals[2]);
                spi_send_byte(vals[3]);
                unselect();

                // set transmit mode
                write_reg(0x01, 0x0C);

                // wait for packet to be sent
                while ((read_reg(0x28) & 0x08) == 0x00);

                // set sleep
                write_reg(0x01, 0x00);
            //}

            watchdog_counter = 0;
        }

        sleep_enable();
        sleep_cpu();
    }

    return 0;
}
