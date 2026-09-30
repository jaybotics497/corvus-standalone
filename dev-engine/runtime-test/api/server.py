#!/usr/bin/env python3
import signal
import time

running = True

def stop(sig, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, stop)

while running:
    time.sleep(0.1)
