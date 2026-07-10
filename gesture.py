import math


def is_pinching(hand_landmarks):


    thumb = hand_landmarks[4]

    index = hand_landmarks[8]


    distance = math.sqrt(
        (thumb.x-index.x)**2 +
        (thumb.y-index.y)**2
    )



    # 阈值

    if distance < 0.08:
        return True

    return False


def finger_up(hand_landmarks):
    """
    判断手指是否伸出

    返回:
    True  食指伸出
    False 非绘画状态
    """


    # 食指

    index_up = (
        hand_landmarks[8].y
        <
        hand_landmarks[6].y
    )


    # 中指

    middle_down = (
        hand_landmarks[12].y
        >
        hand_landmarks[10].y
    )


    # 无名指

    ring_down = (
        hand_landmarks[16].y
        >
        hand_landmarks[14].y
    )


    # 小指

    pinky_down = (
        hand_landmarks[20].y
        >
        hand_landmarks[18].y
    )


    return (
        index_up
        and middle_down

    )

def is_effect(hand):

    fingers = []

    # 大拇指
    if hand[4].x < hand[3].x:
        fingers.append(1)
    else:
        fingers.append(0)


    # 食指
    if hand[8].y < hand[6].y:
        fingers.append(1)
    else:
        fingers.append(0)


    # 中指
    if hand[12].y < hand[10].y:
        fingers.append(1)
    else:
        fingers.append(0)


    # 无名指
    if hand[16].y < hand[14].y:
        fingers.append(1)
    else:
        fingers.append(0)


    # 小指
    if hand[20].y < hand[18].y:
        fingers.append(1)
    else:
        fingers.append(0)


    return sum(fingers) == 5
