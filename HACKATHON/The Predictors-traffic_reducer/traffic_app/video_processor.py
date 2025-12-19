import os
os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'loglevel;quiet|timeout;20000|rtsp_transport;tcp'
os.environ['OPENCV_LOG_LEVEL'] = 'OFF'

import cv2
import yt_dlp
from ultralytics import YOLO
import threading
import time
import numpy as np

class TrafficCamera:
    def __init__(self, youtube_url, model_path='yolov8n.pt'):
        self.youtube_url = youtube_url
        self.model = YOLO(model_path)
        self.video_url = None
        self.cap = None
        self.lock = threading.Lock()
        
      
        self.traffic_state = {
            'norte': 0, 'sur': 0, 'este': 0, 'oeste': 0,
            'pedestrians': 0,
            'emergency': False,
            'frame': None
        }
        
        
        self.zones = {
            'norte': np.array([[0.00, 0.00], [0.12, 0.00], [0.40, 0.50], [0.25, 0.50]]),
            'sur':   np.array([[0.35, 0.75], [0.90, 0.75], [0.90, 1.0], [0.30, 1.0]]),
            'este':  np.array([[0.65, 0.40], [1.0, 0.40], [1.0, 0.70], [0.65, 0.70]]),
            'oeste': np.array([[0.0, 0.55], [0.25, 0.55], [0.25, 0.85], [0.0, 0.85]])
        }
        
        self.current_phase = "INIT"

        self.running = False
        self.thread = threading.Thread(target=self._process_stream)
        self.thread.daemon = True

    def set_phase(self, phase_id):
        
        if phase_id == 0:
            self.current_phase = "NS: GREEN | EW: RED"
        elif phase_id == 1:
            self.current_phase = "NS: RED | EW: GREEN"
        else:
            self.current_phase = f"PHASE: {phase_id}"

    def start(self):
        self.running = True
        self.thread.start()

    def _get_stream_url(self):
        ydl_opts = {
            'format': 'best[protocol^=m3u8]',
            'quiet': True,
            'noplaylist': True,
            'force_ipv4': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.youtube_url, download=False)
                return info['url']
        except Exception as e:
            print(f"yt-dlp error: {e}")
            return None

    def _process_stream(self):
        print("Initializing Traffic Camera Stream...")
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                stream_url = self._get_stream_url()
                if stream_url:
                    self.cap = cv2.VideoCapture(stream_url, cv2.CAP_FFMPEG)
                if not self.cap or not self.cap.isOpened():
                    print("Connection failed. Retrying in 5s...")
                    time.sleep(5)
                    continue
                print("Stream Connected.")

            success, frame = self.cap.read()
            if not success:
                self.cap.release()
                self.cap = None
                time.sleep(1)
                continue

            frame = cv2.resize(frame, (854, 480))
            h, w, _ = frame.shape

            # YOLO: 0=person, 2=car, 3=motorcycle, 5=bus, 7=truck
            results = self.model(frame, verbose=False, classes=[0,2,3,5,7])

            counts = {'norte':0,'sur':0,'este':0,'oeste':0}
            pedestrian_count = 0
            emergency_detected = False

          
            for zone_name, poly in self.zones.items():
                pts = (poly * [w,h]).astype(np.int32)
                cv2.polylines(frame, [pts], True, (0,255,255), 1)
                M = cv2.moments(pts)
                if M['m00'] != 0:
                    cx = int(M['m10']/M['m00']) - 20
                    cy = int(M['m01']/M['m00'])
                    cv2.putText(frame, zone_name.upper(), (cx,cy),
                                cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,255,255),1)

           
            for r in results:
                for box in r.boxes:
                    x1,y1,x2,y2 = box.xyxy[0].cpu().numpy()
                    cx, cy = int((x1+x2)/2), int((y1+y2)/2)
                    cls_id = int(box.cls[0].cpu().numpy())

                    if cls_id == 0:
                        pedestrian_count += 1
                        cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),
                                      (255,255,0),1)
                        continue

                    if cls_id in [5,7]:
                        if (x2-x1)*(y2-y1) > 20000:
                            emergency_detected = True
                            cv2.putText(frame,"EMERGENCY",(int(x1),int(y1)-10),
                                        cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,0,255),2)

                    cv2.circle(frame,(cx,cy),3,(0,0,255),-1)

                    for zone_name, poly in self.zones.items():
                        if cv2.pointPolygonTest((poly * [w,h]).astype(np.int32),(cx,cy),False)>=0:
                            counts[zone_name] += 1
                            cv2.rectangle(frame,(int(x1),int(y1)),(int(x2),int(y2)),
                                          (0,255,0),2)
                            break

            # Info overlay
            cv2.putText(frame,
                        f"N:{counts['norte']} S:{counts['sur']} E:{counts['este']} W:{counts['oeste']}",
                        (20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            cv2.putText(frame,f"Pedestrians: {pedestrian_count}",
                        (20,120),cv2.FONT_HERSHEY_SIMPLEX,0.7,(255,255,0),2)
            if emergency_detected:
                cv2.putText(frame,"EMERGENCY PRIORITY ACTIVE",
                            (20,160),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,0,255),3)
            cv2.putText(frame,f"AI DECISION: {self.current_phase}",
                        (20,80),cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,165,255),2)

            print(f"[DETECTED] {counts} | Peds:{pedestrian_count} | Emergency:{emergency_detected}")

            # Actualizar estado
            with self.lock:
                self.traffic_state.update(counts)
                self.traffic_state['pedestrians'] = pedestrian_count
                self.traffic_state['emergency'] = emergency_detected
                _, buffer = cv2.imencode('.jpg', frame)
                self.traffic_state['frame'] = buffer.tobytes()

    def get_frame(self):
        with self.lock:
            return self.traffic_state['frame']

    def get_counts(self):
        with self.lock:
            return self.traffic_state.copy()
