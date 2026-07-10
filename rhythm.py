import time


class RhythmController:


    def __init__(self):

        self.last_time = 0

        # 当前播放间隔

        self.interval = 0.3



    def update_speed(self, speed):

        """
        根据手移动速度调整节奏
        """

        # 速度越快，间隔越小

        self.interval = 0.5 - speed / 300


        # 限制最快

        if self.interval < 0.12:

            self.interval = 0.12



        # 限制最慢

        if self.interval > 0.5:

            self.interval = 0.5



    def can_play(self):


        current = time.time()


        if current - self.last_time > self.interval:


            self.last_time = current

            return True


        return False