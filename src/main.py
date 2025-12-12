# main.py
import time
import threading
from camera_detection import start_camera_thread
from sound_detection import start_audio_thread
from traffic_controller import controller
from ui_simulation import TrafficUI
from utils import shared_state

def main_loop():
    # start sensors
    start_camera_thread(0)
    start_audio_thread()

    ui = TrafficUI(1100, 700)
    running = True

    try:
        while running:
            # Pygame event handling
            for event in __import__("pygame").event.get():
                if event.type == __import__("pygame").QUIT:
                    running = False

            # update controller
            lights, mode, pr = controller.update()

            # render UI
            ui.draw(lights, mode, pr)

            # small sleep to free CPU a bit
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        ui.quit()
        print("Exiting...")

if __name__ == "__main__":
    main_loop()
