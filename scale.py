import math


# 十二平均律基准
A4 = 440


def note_to_frequency(note):

    """
    note:
    MIDI编号

    返回频率
    """

    frequency = A4 * (
        2 ** ((note - 69) / 12)
    )

    return frequency



class Scale:


    def __init__(self):

        # C4开始

        self.root = 60



        # 三种音阶

        self.major = [
            0,2,4,5,7,9,11
        ]


        self.minor = [
            0,2,3,5,7,8,10
        ]


        self.pentatonic = [
            0,2,4,7,9
        ]



    def get_notes(self, name):

        if name=="MAJOR":

            scale=self.major


        elif name=="MINOR":

            scale=self.minor


        else:

            scale=self.pentatonic



        notes=[]


        for step in scale:

            notes.append(
                self.root+step
            )


        return notes

    def get_chord(
            self,
            scale_name,
            root
    ):

        if scale_name == "MAJOR":

            return [
                root,
                root + 4,
                root + 7
            ]

        elif scale_name == "MINOR":

            return [
                root,
                root + 3,
                root + 7
            ]

        else:

            return [
                root,
                root + 2,
                root + 7
            ]

def speed_to_note(
        speed,
        notes
):

    """
    根据速度选择音符

    speed:
    0~100

    notes:
    当前音阶列表
    """


    # 限制速度

    speed = max(
        0,
        min(speed,100)
    )


    # 根据速度选择索引

    index = int(
        speed / 100 * len(notes)
    )


    # 防止越界

    if index >= len(notes):

        index = len(notes)-1


    return notes[index]