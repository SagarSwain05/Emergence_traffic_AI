# ui_simulation.py
import pygame
import cv2
import numpy as np
from utils import shared_state

# Pygame colors
COLORS = {
    "RED": (200, 0, 0),
    "YELLOW": (220, 180, 0),
    "GREEN": (0, 160, 0),
    "GRAY": (50, 50, 50),
    "BG": (30, 30, 40),
    "WHITE": (255,255,255)
}

def cvimage_to_pygame(image):
    # Convert BGR (OpenCV) to RGB then to Pygame surface
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.rot90(image)  # optional rotate to fit UI nicely
    surface = pygame.surfarray.make_surface(image)
    return surface

def draw_detections_on_frame(frame, detections):
    """Draw bounding boxes and labels on frame."""
    frame_copy = frame.copy()
    for det in detections:
        x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]
        label = det["label"]
        conf = det["conf"]
        is_emergency = det["is_emergency"]
        
        # Use bright color for emergency, dim for others
        if is_emergency:
            color = (0, 0, 255)  # Red in BGR
            thickness = 3
        else:
            color = (0, 255, 0)  # Green in BGR
            thickness = 2
        
        # Draw rectangle
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, thickness)
        
        # Draw label with confidence
        label_text = f"{label} {conf:.2f}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness_text = 1
        text_size = cv2.getTextSize(label_text, font, font_scale, thickness_text)[0]
        
        # Background for text
        cv2.rectangle(frame_copy, (x1, y1 - text_size[1] - 4),
                     (x1 + text_size[0] + 4, y1), color, -1)
        
        # Draw text
        cv2.putText(frame_copy, label_text, (x1 + 2, y1 - 2),
                   font, font_scale, (255, 255, 255), thickness_text)
    
    return frame_copy

class TrafficUI:
    def __init__(self, w=1000, h=700):
        pygame.init()
        self.w, self.h = w, h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Emergency Traffic Priority Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18)
        self.bigfont = pygame.font.SysFont("Arial", 28, bold=True)

    def draw(self, lights, mode, priority_lane):
        self.screen.fill(COLORS["BG"])
        center_x = self.w//2
        center_y = self.h//2

        road_w = 160
        # draw roads (simple cross)
        pygame.draw.rect(self.screen, (40,40,40), (center_x-road_w//2, 0, road_w, self.h))
        pygame.draw.rect(self.screen, (40,40,40), (0, center_y-road_w//2, self.w, road_w))

        # draw traffic lights near each corner of intersection
        # north light position
        offset = 120
        light_positions = {
            "N": (center_x - 30, center_y - road_w//2 - offset),
            "S": (center_x + 30, center_y + road_w//2 + offset),
            "E": (center_x + road_w//2 + offset, center_y - 30),
            "W": (center_x - road_w//2 - offset, center_y + 30)
        }

        for lane, pos in light_positions.items():
            # draw box
            pygame.draw.rect(self.screen, (20,20,20), (pos[0]-18, pos[1]-18, 36, 54), border_radius=6)
            # three lights: red,yellow,green vertical/horizontal
            # determine color order based on lane orientation
            state = lights.get(lane, "RED")
            # draw circles
            # vertical stack
            cx = pos[0]
            cy = pos[1]
            r = 8
            # red
            pygame.draw.circle(self.screen, COLORS["RED"] if state=="RED" else (60,0,0), (cx, cy-14), r)
            # yellow
            pygame.draw.circle(self.screen, COLORS["YELLOW"] if state=="YELLOW" else (60,60,0), (cx, cy), r)
            # green
            pygame.draw.circle(self.screen, COLORS["GREEN"] if state=="GREEN" else (0,40,0), (cx, cy+14), r)

            # lane label
            lbl = self.font.render(lane, True, COLORS["WHITE"])
            self.screen.blit(lbl, (pos[0]-lbl.get_width()//2, pos[1]+26))

        # show mode and priority
        mode_text = f"Mode: {mode}"
        self.screen.blit(self.bigfont.render(mode_text, True, COLORS["WHITE"]), (20,20))
        if mode == "PRIORITY" and priority_lane:
            pr_text = f"PRIORITY LANE: {priority_lane}"
            self.screen.blit(self.bigfont.render(pr_text, True, (255,200,0)), (20, 60))

        # show small camera preview if available
        with shared_state.lock:
            frame = shared_state.camera_frame.copy() if shared_state.camera_frame is not None else None
            detections = shared_state.detections.copy() if shared_state.detections else []
            siren_flag = shared_state.siren_detected

        if frame is not None:
            # Draw bounding boxes on frame
            frame_with_boxes = draw_detections_on_frame(frame, detections)
            
            # convert and scale
            hf, wf = 180, 240
            frame_small = cv2.resize(frame_with_boxes, (wf, hf))
            surf = cvimage_to_pygame(frame_small)
            # blit top-right
            self.screen.blit(surf, (self.w - wf - 20, 20))
            cv_label = self.font.render("Camera Preview (with detections)", True, COLORS["WHITE"])
            self.screen.blit(cv_label, (self.w - wf - 20, hf + 24))

            # overlay siren indicator
            siren_label = self.font.render(f"Siren: {'YES' if siren_flag else 'NO'}", True, (255,100,100) if siren_flag else COLORS["WHITE"])
            self.screen.blit(siren_label, (self.w - wf - 20, hf + 48))

        pygame.display.flip()
        self.clock.tick(30)

    def quit(self):
        pygame.quit()
