import cv2
import mediapipe as mp
import random
import audio
import wave

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from gesture import (finger_up,is_pinching)
from motion import calculate_speed,smooth_speed
from audio import play_speed_sound
from rhythm import RhythmController
from state import ChromaState

from scale import Scale, speed_to_note
from audio import play_note
from trajectory import get_motion_type

import numpy as np
import rhythm
from audio import play_chord
from audio import save_record
from particles import (create_particles,update_particles,create_glow)
import time
import music_engine


# =========================
# 1. 创建手部检测器
# =========================

model_path = "hand_landmarker.task"

base_options = python.BaseOptions(
    model_asset_path=model_path
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=1
)

detector = vision.HandLandmarker.create_from_options(options)


# =========================
# 2. 手部骨架连接关系
# =========================

connections = [
    (0,1),(1,2),(2,3),(3,4),       # 大拇指

    (0,5),(5,6),(6,7),(7,8),       # 食指

    (0,9),(9,10),(10,11),(11,12), # 中指

    (0,13),(13,14),(14,15),(15,16), # 无名指

    (0,17),(17,18),(18,19),(19,20), # 小指

    (5,9),(9,13),(13,17)           # 手掌
]


# =========================
# 3. 打开摄像头
# =========================

cap = cv2.VideoCapture(0)
melody_rhythm = RhythmController()


chord_rhythm = RhythmController()
state = ChromaState()
scale = Scale()
melody_index = 0
canvas = None
trail = None
particle_layer = None
background_layer = None

pinch_last = False
pinch_count = 0

mode="IDLE"

prev_x = None
prev_y = None

current_brush_size=5
draw_lost_count = 0

smooth_x = None
smooth_y = None
music=music_engine.MusicEngine()

while True:

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    if canvas is None:
        canvas = np.ones_like(frame)*255
    if trail is None:
        trail = np.zeros_like(frame)
    if particle_layer is None:
        particle_layer = np.zeros_like(frame)
    if background_layer is None:
        background_layer = np.zeros_like(frame)

    particle_layer[:] = 0
    background_layer = (
            background_layer * 0.96
    ).astype(np.uint8)



    if not ret:
        break

    # OpenCV BGR 转 RGB

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )
    # 转成 MediaPipe Image

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    # 检测

    result = detector.detect(mp_image)

    # =========================
    # 4. 绘制21个关键点
    # =========================

    if result.hand_landmarks:
        from gesture import finger_up

        for hand in result.hand_landmarks:

            index_tip = hand[8]

            index_x = int(
                index_tip.x *
                frame.shape[1]
            )

            index_y = int(
                index_tip.y *
                frame.shape[0]
            )

            # =========================
            # 坐标平滑（EMA）
            # =========================

            if smooth_x is None:

                smooth_x = index_x
                smooth_y = index_y

            else:

                alpha = 0.35  # 越小越平滑，越大越跟手

                smooth_x = int(
                    alpha * index_x +
                    (1 - alpha) * smooth_x
                )

                smooth_y = int(
                    alpha * index_y +
                    (1 - alpha) * smooth_y
                )


            cv2.circle(
                frame,
                (smooth_x, smooth_y),
                6,
                (255, 255, 255),
                -1
            )



            if is_pinching(hand):
                pinch_count+=1
                mode="PINCH"

                cv2.putText(
                    frame,
                    "PINCH",
                    (100, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    3,
                    (0, 255, 0),
                    2
                )
                if pinch_count>=10:
                    if not pinch_last:
                        state.change_mode()


                        pinch_last = True





                cv2.putText(
                    frame,
                    state.get_scale(),
                    (50, 150),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    state.get_color(),
                    2
                )

            elif finger_up(hand):
                pinch_last = False
                pinch_count = 0
                mode="DRAW"

                cv2.putText(
                    frame,
                    "DRAW MODE",
                    (100, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    3,
                    (0, 255, 0),
                    2
                )




            else:
                pinch_last = False
                pinch_count=0
                mode="IDLE"


                cv2.putText(
                    frame,
                    "IDLE",
                    (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )


            points=[]


            # 坐标转换

            for idx, landmark in enumerate(hand):

                x = int(
                    landmark.x *
                    frame.shape[1]
                )

                y = int(
                    landmark.y *
                    frame.shape[0]
                )

                points.append((x,y))

            #========================
            #从这里开始是绘画区
            #========================

            if finger_up(hand):

                draw_lost_count = 0


                speed = calculate_speed(
                    smooth_x,
                    smooth_y,
                    prev_x,
                    prev_y
                )

                motion_type = get_motion_type(
                    prev_x,
                    prev_y,
                    smooth_x,
                    smooth_y
                )



                speed = smooth_speed(speed)
                if speed > 3 :




                    if motion_type == "HORIZONTAL":

                        melody_rhythm.update_speed(speed)

                        if melody_rhythm.can_play():


                            notes = scale.get_notes(
                                state.get_scale()
                            )


                            if len(notes) == 0:
                                continue

                            if melody_index >= len(notes):
                                melody_index = 0

                            note_index = int(
                                smooth_x / canvas.shape[1] * len(notes)
                            )

                            note_index = min(
                                max(note_index, 0),
                                len(notes) - 1
                            )

                            note = notes[note_index]



                            melody_index += 1

                            volume = max(0.01, min(speed / 400 ,0.22))

                            music.play_note_event(
                                note,
                                state,
                                volume
                            )

                            background_strength = int(
                                volume * 120
                            )

                            glow_x = random.randint(
                                100,
                                output.shape[1] - 100
                            )

                            glow_y = random.randint(
                                100,
                                output.shape[0] - 100
                            )

                            create_glow(
                                background_layer,
                                glow_x,
                                glow_y,
                                120,
                                state.get_color()
                            )

                            particle_count = int(
                                max(
                                    5,
                                    min(speed / 4, 30)
                                )
                            )

                            create_particles(
                                smooth_x,
                                smooth_y,
                                state.get_color(),
                                particle_count,speed/30
                            )













                    elif motion_type == "VERTICAL":

                        chord_rhythm.update_speed(speed)

                        if chord_rhythm.can_play():

                            notes = scale.get_notes(
                                state.get_scale()
                            )
                            if melody_index >= len(notes):
                                melody_index = 0

                            id = "8sgw9y"
                            note_index = int(
                                smooth_y / canvas.shape[0] * len(notes)
                            )

                            note_index = min(
                                max(note_index, 0),
                                len(notes) - 1
                            )

                            root = notes[note_index]


                            chord = scale.get_chord(
                                state.get_scale(),
                                root
                            )


                            chord_volume = max(
                                0.005,
                                min(speed / 500, 0.03)
                            )

                            play_chord(

                                chord,

                                state.get_instrument(),

                                chord_volume

                            )
                            glow_x = random.randint(
                                100,
                                output.shape[1] - 100
                            )

                            glow_y = random.randint(
                                100,
                                output.shape[0] - 100
                            )

                            create_glow(
                                background_layer,
                                glow_x,
                                glow_y,
                                120,
                                state.get_color()
                            )

                            particle_count = int(
                                max(
                                    5,
                                    min(speed / 4, 30)
                                )
                            )

                            create_particles(
                                smooth_x,
                                smooth_y,
                                state.get_color(),
                                particle_count,speed/30
                            )




                cv2.putText(
                    frame,
                    f"Speed:{int(speed)}",
                    (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 255),
                    2
                )

                target_brush_size = max(
                    2,
                    min(speed / 8, 14)
                )

                current_brush_size = (
                        current_brush_size * 0.7
                        +
                        target_brush_size * 0.3
                )

                brush_size = int(current_brush_size)
                # canvas = (
                #         canvas * 0.995
                # ).astype(np.uint8)

                if prev_x is not None and mode=="DRAW" and mode!="PINCH":

                    cv2.line(
                        trail,
                        (prev_x, prev_y),
                        (smooth_x, smooth_y),
                        state.get_color(),
                        brush_size
                    )

                prev_x = smooth_x
                prev_y = smooth_y

            else:
                draw_lost_count += 1

                prev_x = None
                prev_y = None

                smooth_x = None
                smooth_y = None

                # 画点




                # 显示编号

                cv2.putText(
                    frame,
                    str(idx),
                    (x+5,y-5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255,0,0),
                    1
                )


            # =====================
            # 绘制骨架
            # =====================



            for start,end in connections:

                cv2.line(
                    frame,
                    points[start],
                    points[end],
                    (0,0,255),
                    2
                )



    # 显示

    frame = cv2.add(frame, trail)

    update_particles(particle_layer)

    # 白色背景
    output = canvas.copy()

    # 加入背景光晕
    bg_mask = cv2.cvtColor(
        background_layer,
        cv2.COLOR_BGR2GRAY
    )

    blend = cv2.addWeighted(
        output,
        0.7,
        background_layer,
        0.3,
        0
    )

    output[bg_mask > 0] = blend[bg_mask > 0]





    # 加入画笔轨迹
    mask = cv2.cvtColor(
        trail,
        cv2.COLOR_BGR2GRAY
    )

    output[mask > 0] = trail[mask > 0]

    # 加入粒子
    mask = cv2.cvtColor(
        particle_layer,
        cv2.COLOR_BGR2GRAY
    )

    output[mask > 0] = particle_layer[mask > 0]

    # 摄像头缩小
    camera_small = cv2.resize(
        frame,
        (240, 180)
    )

    h, w, _ = output.shape

    output[
        h - 180:h,
        w - 240:w
    ] = camera_small











    cv2.imshow(
        "MediaPipe Hand 21 Points",
        output
    )


    # ESC退出

    key = cv2.waitKey(1)

    if key == 27:
        break

    if key == ord('s'):



        audio.recording = not audio.recording

        if audio.recording:
            audio.record_buffer.clear()
            print("开始录音")

        else:
            cv2.imwrite(
                "painting.png",
                output
            )

            print("painting saved")

            audio.save_record(
                "music.wav"
            )

            print("结束录音")



cap.release()
cv2.destroyAllWindows()

ret