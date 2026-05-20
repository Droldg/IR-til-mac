from machine import Pin, time_pulse_us
import time

IR_PIN = 15
LED_PIN = "LED"
LED_BLINK_MS = 80

SHUTDOWN_COMMAND = "SHUTDOWN"
ACTION_COOLDOWN_MS = 1500

ir = Pin(IR_PIN, Pin.IN)
led = Pin(LED_PIN, Pin.OUT)

APPLE_REMOTE = {
    0x475D: "Ok",
    0x470D: "Ned",
    0x470B: "Op",
    0x4708: "Venstre",
    0x4707: "Hoejre",
    0x475E: "Pause",
    0x4702: "Menu",
}

EXPECTED_ADDRESS = 0x87EE


def read_nec():
    # Wait for start pulse. The IR receiver is normally HIGH and goes LOW.
    while ir.value() == 1:
        pass

    # NEC start: about 9000 us LOW, 4500 us HIGH.
    start_low = time_pulse_us(ir, 0, 20000)
    start_high = time_pulse_us(ir, 1, 20000)

    if start_low < 8000 or start_low > 10000:
        return None

    # Repeat code is typically 9000 LOW + 2250 HIGH.
    if 1800 < start_high < 2800:
        return "REPEAT"

    if start_high < 3500 or start_high > 5500:
        return None

    bits = []

    for _ in range(32):
        low = time_pulse_us(ir, 0, 2000)
        high = time_pulse_us(ir, 1, 3000)

        if low < 300 or low > 800:
            return None

        # NEC: short HIGH around 560 us = 0, long HIGH around 1690 us = 1.
        if 300 < high < 900:
            bits.append(0)
        elif 1200 < high < 2200:
            bits.append(1)
        else:
            return None

    value = 0
    for i, bit in enumerate(bits):
        value |= bit << i

    address = value & 0xFFFF
    command = (value >> 16) & 0xFFFF

    return address, command, value


def write_shutdown_command():
    print(SHUTDOWN_COMMAND)


def blink_led():
    led.value(1)
    time.sleep_ms(LED_BLINK_MS)
    led.value(0)


def handle_button(name):
    if name == "Pause":
        write_shutdown_command()
        return True

    return False


print("Klar til at laese Apple IR remote paa GPIO{}".format(IR_PIN))
print("Peg fjernbetjeningen mod IR-modtageren og tryk paa en knap.")
print()

last_command = None
last_action_time = 0

while True:
    result = read_nec()

    if result is None:
        continue

    if result == "REPEAT":
        if last_command is not None:
            print("Gentag:", last_command)
        continue

    address, command, raw = result
    blink_led()

    name = APPLE_REMOTE.get(command, "Ukendt knap")

    print("Raw:     0x{:08X}".format(raw))
    print("Address: 0x{:04X}".format(address))
    print("Command: 0x{:04X}".format(command))
    print("Knap:   {}".format(name))

    if address != EXPECTED_ADDRESS:
        print("Advarsel: Address matcher ikke Apple.ir-filen")
    else:
        now = time.ticks_ms()
        if time.ticks_diff(now, last_action_time) > ACTION_COOLDOWN_MS:
            if handle_button(name):
                last_action_time = now

    print("-" * 30)

    last_command = name
    time.sleep(0.15)
