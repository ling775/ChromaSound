import math
from collections import deque


# 保存最近几帧速度
speed_history = deque(maxlen=5)



def calculate_speed(
        x,
        y,
        prev_x,
        prev_y
):

    if prev_x is None or prev_y is None:
        return 0


    distance = math.sqrt(
        (x-prev_x)**2 +
        (y-prev_y)**2
    )


    return distance



def smooth_speed(speed):

    speed_history.append(speed)


    average = sum(speed_history) / len(speed_history)


    return average