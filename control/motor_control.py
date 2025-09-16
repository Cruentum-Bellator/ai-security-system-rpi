import time

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except Exception:
    GPIO_AVAILABLE = False
    class DummyGPIO:
        BCM = OUT = None
        def setmode(self, *_): pass
        def setup(self, *_): pass
        def output(self, *_): pass
        def cleanup(self): pass
    GPIO = DummyGPIO()

SEQ_HALFSTEP = [
    [1,0,0,1],
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1]
]

class StepMotor:
    def __init__(self, pins, step_delay=0.002):
        self.pins = pins
        self.step_delay = step_delay
        self.dir = 1
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            for p in pins:
                GPIO.setup(p, GPIO.OUT)
                GPIO.output(p, 0)

    def set_dir(self, d):
        self.dir = 1 if d >= 0 else -1

    def step(self, steps):
        if not GPIO_AVAILABLE:
            return
        direction = 1 if steps >= 0 else -1
        order = SEQ_HALFSTEP if direction * self.dir > 0 else SEQ_HALFSTEP[::-1]
        n = abs(int(steps))
        for _ in range(n):
            for half in order:
                for pin, val in zip(self.pins, half):
                    GPIO.output(pin, val)
                time.sleep(self.step_delay)

    def cleanup(self):
        if GPIO_AVAILABLE:
            GPIO.cleanup()
