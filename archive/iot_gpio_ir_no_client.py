import time
from gpiozero import LED, MotionSensor, Buzzer
motion_sensor = MotionSensor(4)
led = LED(2)
buzzer = Buzzer(17)

try:
    while True:
        motion_sensor.wait_for_active()
        print("Motion detected")
        buzzer.beep(n=2)
        led.blink(n=2)
        time.sleep(2)
finally:
    buzzer.off()
    led.off()

