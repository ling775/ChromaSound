

def get_motion_type(
        prev_x,
        prev_y,
        current_x,
        current_y
):

    if prev_x is None or prev_y is None:
        return "NONE"



    dx = current_x - prev_x
    dy = current_y - prev_y


    abs_dx = abs(dx)
    abs_dy = abs(dy)



    # 过滤微小抖动

    if abs_dx < 5 and abs_dy < 5:

        return "NONE"



    # 方向优势比例

    threshold = 1.5



    # 明显水平

    if abs_dx > abs_dy * threshold:

        return "HORIZONTAL"



    # 明显垂直

    elif abs_dy > abs_dx * threshold:

        return "VERTICAL"



    # 不确定方向

    else:

        return "NONE"