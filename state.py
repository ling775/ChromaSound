##颜色变量和音阶变量

class ChromaState:


    def __init__(self):

        # 当前颜色

        self.colors = [
            (104,172,255),     # 红
            (255,127,31),     # 蓝
            (193,255,139)      # 绿
        ]


        # 当前索引

        self.index = 0



        # 对应音阶

        self.scales = [
            "MAJOR",
            "MINOR",
            "PENTATONIC"
        ]



    def change_mode(self):

        self.index += 1


        if self.index >= len(self.colors):

            self.index = 0



    def get_color(self):

        return self.colors[self.index]



    def get_scale(self):

        return self.scales[self.index]

    def get_instrument(self):
        instruments = [
            "piano",
            "pad",
            "bell"
        ]

        return instruments[self.index]

    def get_accompaniment(self):
        instruments = [
            "pad",
            "strings",
            "bass"
        ]

        return instruments[self.index]

    def get_rhythm(self):
        rhythms = [
            "slow",
            "medium",
            "fast"
        ]

        return rhythms[self.index]