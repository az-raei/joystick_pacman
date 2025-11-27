# Pac-Man Controlled by Arduino Joystick

A classic **Pac-Man clone in Python (pygame)** controlled using a **physical analog joystick connected to an Arduino**, communicating with the game over **serial (USB)**.

This project combines **embedded systems**, **serial communication**, and **game development** into a fun, interactive demo.

---

## Demo
- Move Pac-Man using a **hardware joystick**
- Eat pellets to increase score
- Avoid ghosts
- Button press increases movement speed

---

## System Architecture
Joystick → Arduino → Serial (USB) → Python → Pygame Window


- **Arduino** reads analog joystick values
- Sends X, Y, and button state over serial
- **Python** parses serial data
- **Pygame** updates Pac-Man movement in real time

---

## Hardware Used

- Arduino Uno
- Analog joystick module (VRx, VRy, SW)
- USB cable (Arduino -> PC)
- Laptop

---

## Wiring Diagram (Arduino)

| Joystick Pin | Arduino Pin |
|-------------|-------------|
| VCC         | 5V          |
| GND         | GND         |
| VRx         | A0          |
| VRy         | A1          |
| SW          | D2          |

---

## Software Used

- **Python 3**
- **Pygame**
- **PySerial**
- Arduino IDE

---

## Dependencies

Install Python libraries:

```bash
pip install pygame pyserial
