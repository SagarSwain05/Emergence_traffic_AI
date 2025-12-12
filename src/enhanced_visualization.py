# enhanced_visualization.py
"""
Enhanced visualization with confidence scores, detection info panel,
lane mapping visualization, and detailed analytics.

Can be used as an alternative to ui_simulation.py for more detailed display.
"""

import pygame
import cv2
import numpy as np
from utils import shared_state
import time

COLORS = {
    "RED": (200, 0, 0),
    "YELLOW": (220, 180, 0),
    "GREEN": (0, 160, 0),
    "EMERGENCY": (255, 100, 0),
    "BG": (20, 20, 30),
    "WHITE": (255, 255, 255),
    "TEXT_DIM": (150, 150, 150),
}

def cvimage_to_pygame(image):
    """Convert OpenCV BGR image to Pygame surface."""
    if image is None:
        return None
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = np.rot90(image)
    surface = pygame.surfarray.make_surface(image)
    return surface

def draw_detection_overlay_advanced(frame, detections):
    """Draw advanced detection overlay with confidence, class info, and lane zones."""
    frame_copy = frame.copy()
    h, w = frame.shape[:2]
    
    # Draw lane zones as semi-transparent regions
    zones = {
        "N": (0, 0, w, int(h * 0.35), (100, 100, 200)),
        "S": (0, int(h * 0.65), w, h, (100, 200, 100)),
        "W": (0, 0, int(w * 0.35), h, (200, 100, 100)),
        "E": (int(w * 0.65), 0, w, h, (200, 200, 100)),
    }
    
    # Draw zone overlays (very transparent)
    overlay = frame_copy.copy()
    for zone_name, (x1, y1, x2, y2, color) in zones.items():
        cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
        cv2.putText(overlay, zone_name, (x1 + 10, y1 + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, color, 2)
    cv2.addWeighted(overlay, 0.08, frame_copy, 0.92, 0, frame_copy)
    
    # Draw detection boxes
    for det in detections:
        x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]
        label = det["label"]
        conf = det["conf"]
        is_emergency = det["is_emergency"]
        
        # Color based on emergency status
        if is_emergency:
            color = (0, 0, 255)  # Red for emergency
            thickness = 3
        else:
            color = (0, 255, 0)  # Green for other
            thickness = 2
        
        # Main bounding box
        cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, thickness)
        
        # Draw center point
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(frame_copy, (cx, cy), 5, color, -1)
        
        # Confidence bar
        box_w = x2 - x1
        bar_y = y2 + 5
        bar_h = 8
        conf_w = int(box_w * conf)
        cv2.rectangle(frame_copy, (x1, bar_y), (x1 + conf_w, bar_y + bar_h), color, -1)
        cv2.rectangle(frame_copy, (x1, bar_y), (x2, bar_y + bar_h), color, 1)
        
        # Label with confidence and class
        label_text = f"{label} {conf:.2%}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        text_size = cv2.getTextSize(label_text, font, font_scale, 1)[0]
        
        # Background for label
        label_y = y1 - 8
        cv2.rectangle(frame_copy, (x1, label_y - text_size[1] - 4),
                     (x1 + text_size[0] + 4, label_y), color, -1)
        cv2.putText(frame_copy, label_text, (x1 + 2, label_y - 2),
                   font, font_scale, (255, 255, 255), 1)
    
    return frame_copy

class EnhancedTrafficUI:
    """Advanced traffic UI with detailed analytics and visualization."""
    
    def __init__(self, w=1400, h=900):
        pygame.init()
        self.w, self.h = w, h
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("Emergency Traffic Priority - Enhanced View")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Courier", 14)
        self.font_big = pygame.font.SysFont("Courier", 20, bold=True)
        self.font_huge = pygame.font.SysFont("Courier", 32, bold=True)
        
        # Stats history for graphs
        self.detection_history = []
        self.siren_history = []
        self.max_history = 120  # 4 seconds at 30 FPS
    
    def update_history(self, ambulance_detected, siren_detected):
        """Update detection history for visualization."""
        self.detection_history.append(1 if ambulance_detected else 0)
        self.siren_history.append(1 if siren_detected else 0)
        
        if len(self.detection_history) > self.max_history:
            self.detection_history.pop(0)
            self.siren_history.pop(0)
    
    def draw_detection_panel(self, x, y, w, h, detections):
        """Draw panel showing all detected objects with details."""
        # Background
        pygame.draw.rect(self.screen, (20, 20, 40), (x, y, w, h))
        pygame.draw.rect(self.screen, (100, 100, 150), (x, y, w, h), 2)
        
        # Title
        title = self.font_big.render("Detections", True, COLORS["WHITE"])
        self.screen.blit(title, (x + 10, y + 5))
        
        # Detections list
        line_h = 22
        for i, det in enumerate(detections[:5]):  # Show top 5
            yi = y + 30 + i * line_h
            if yi > y + h - 20:
                break
            
            # Color indicator
            color_rect = pygame.Rect(x + 10, yi, 12, 12)
            det_color = COLORS["EMERGENCY"] if det["is_emergency"] else (100, 200, 100)
            pygame.draw.rect(self.screen, det_color, color_rect)
            
            # Text
            text = f"{det['label'][:15]:15} {det['conf']:.1%} ({det['x2']-det['x1']}px)"
            txt = self.font.render(text, True, COLORS["WHITE"])
            self.screen.blit(txt, (x + 30, yi - 2))
        
        if not detections:
            txt = self.font.render("No detections", True, COLORS["TEXT_DIM"])
            self.screen.blit(txt, (x + 10, y + 40))
    
    def draw_timeline_graph(self, x, y, w, h, data, label, color):
        """Draw a simple timeline graph."""
        # Background
        pygame.draw.rect(self.screen, (20, 20, 40), (x, y, w, h))
        pygame.draw.rect(self.screen, color, (x, y, w, h), 1)
        
        # Title
        title = self.font.render(label, True, color)
        self.screen.blit(title, (x + 5, y + 2))
        
        # Draw graph line
        if len(data) > 1:
            scale_h = h - 20
            for i in range(len(data) - 1):
                x1 = x + (i / len(data)) * w
                y1 = y + h - data[i] * scale_h - 3
                x2 = x + ((i + 1) / len(data)) * w
                y2 = y + h - data[i + 1] * scale_h - 3
                pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)
    
    def draw_lane_indicators(self, x, y, lights, priority_lane):
        """Draw lane status indicators."""
        lanes = ["N", "E", "S", "W"]
        size = 50
        spacing = 15
        
        for i, lane in enumerate(lanes):
            xi = x + i * (size + spacing)
            
            # Box
            state = lights.get(lane, "RED")
            state_color = {
                "RED": COLORS["RED"],
                "YELLOW": COLORS["YELLOW"],
                "GREEN": COLORS["GREEN"]
            }.get(state, (100, 100, 100))
            
            pygame.draw.rect(self.screen, state_color, (xi, y, size, size))
            border_color = COLORS["EMERGENCY"] if lane == priority_lane else (100, 100, 100)
            pygame.draw.rect(self.screen, border_color, (xi, y, size, size), 3)
            
            # Lane label
            txt = self.font_big.render(lane, True, COLORS["WHITE"])
            txt_rect = txt.get_rect(center=(xi + size // 2, y + size // 2))
            self.screen.blit(txt, txt_rect)
    
    def draw(self, lights, mode, priority_lane, detections, ambulance_detected, siren_detected):
        """Draw the enhanced UI."""
        self.screen.fill(COLORS["BG"])
        
        # Update history
        self.update_history(ambulance_detected, siren_detected)
        
        # Title bar
        title_surf = self.font_huge.render("Emergency Traffic AI - Enhanced", True, COLORS["WHITE"])
        self.screen.blit(title_surf, (20, 10))
        
        # Mode indicator
        mode_text = f"MODE: {mode}"
        mode_color = COLORS["EMERGENCY"] if mode == "PRIORITY" else (100, 200, 100)
        mode_surf = self.font_big.render(mode_text, True, mode_color)
        self.screen.blit(mode_surf, (self.w - 300, 15))
        
        # Priority lane
        if priority_lane:
            pr_text = f"Priority: {priority_lane}"
            pr_surf = self.font_big.render(pr_text, True, COLORS["EMERGENCY"])
            self.screen.blit(pr_surf, (self.w - 300, 45))
        
        # Lane indicators (top section)
        self.draw_lane_indicators(20, 70, lights, priority_lane)
        
        # Camera feed with enhanced overlay (left side)
        cam_x, cam_y, cam_w, cam_h = 20, 150, 600, 450
        with shared_state.lock:
            frame = shared_state.camera_frame.copy() if shared_state.camera_frame is not None else None
            detections = shared_state.detections.copy() if shared_state.detections else []
        
        if frame is not None:
            # Draw advanced overlay
            frame_overlay = draw_detection_overlay_advanced(frame, detections)
            frame_resized = cv2.resize(frame_overlay, (cam_w, cam_h))
            surf = cvimage_to_pygame(frame_resized)
            self.screen.blit(surf, (cam_x, cam_y))
            
            # Border
            pygame.draw.rect(self.screen, (100, 200, 100), (cam_x, cam_y, cam_w, cam_h), 2)
            
            # Label
            cam_label = self.font_big.render("Camera Feed", True, COLORS["WHITE"])
            self.screen.blit(cam_label, (cam_x + 10, cam_y + cam_h + 10))
        
        # Detection panel (right side)
        det_x, det_y, det_w, det_h = 650, 150, 350, 200
        self.draw_detection_panel(det_x, det_y, det_w, det_h, detections)
        
        # Status panel
        status_x, status_y, status_w, status_h = 650, 370, 350, 230
        pygame.draw.rect(self.screen, (20, 20, 40), (status_x, status_y, status_w, status_h))
        pygame.draw.rect(self.screen, (150, 100, 100), (status_x, status_y, status_w, status_h), 2)
        
        title_txt = self.font_big.render("Status", True, COLORS["WHITE"])
        self.screen.blit(title_txt, (status_x + 10, status_y + 5))
        
        y_offset = status_y + 35
        line_h = 25
        
        # Status items
        det_status = "YES" if ambulance_detected else "NO"
        det_color = COLORS["EMERGENCY"] if ambulance_detected else (100, 100, 100)
        txt1 = self.font.render(f"Ambulance: {det_status}", True, det_color)
        self.screen.blit(txt1, (status_x + 15, y_offset))
        
        y_offset += line_h
        siren_status = "YES" if siren_detected else "NO"
        siren_color = COLORS["EMERGENCY"] if siren_detected else (100, 100, 100)
        txt2 = self.font.render(f"Siren: {siren_status}", True, siren_color)
        self.screen.blit(txt2, (status_x + 15, y_offset))
        
        y_offset += line_h
        lane_text = priority_lane if priority_lane else "None"
        txt3 = self.font.render(f"Priority Lane: {lane_text}", True, COLORS["WHITE"])
        self.screen.blit(txt3, (status_x + 15, y_offset))
        
        y_offset += line_h
        det_count = len(detections)
        txt4 = self.font.render(f"Objects Detected: {det_count}", True, COLORS["WHITE"])
        self.screen.blit(txt4, (status_x + 15, y_offset))
        
        # Timeline graphs (bottom)
        graph_y = 620
        self.draw_timeline_graph(20, graph_y, 400, 80, self.detection_history, "Ambulance", COLORS["EMERGENCY"])
        self.draw_timeline_graph(440, graph_y, 400, 80, self.siren_history, "Siren", (255, 200, 0))
        
        # Info footer
        fps = self.clock.get_fps()
        footer = self.font.render(f"FPS: {fps:.1f} | Detections: {len(detections)} | Mode: {mode}", True, COLORS["TEXT_DIM"])
        self.screen.blit(footer, (20, self.h - 25))
        
        pygame.display.flip()
        self.clock.tick(30)
    
    def quit(self):
        pygame.quit()
