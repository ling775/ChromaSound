import random
import math
import numpy as np
import cv2

particles = []


class Particle:

    def __init__(
            self,
            x,
            y,
            color,
            power=1
    ):

        self.x = x
        self.y = y

        self.color = color
        self.size = random.randint(2, 6)


        angle = random.uniform(
            0,
            math.pi * 2
        )


        speed = random.uniform(
            0.5,
            3
        )*power


        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed


        self.life = 30



    def update(self):

        self.x += self.vx
        self.y += self.vy


        self.life -= 1



    def draw(self, frame):

        if self.life > 0:

            import cv2

            radius = max(
                1,
                int(self.size * self.life / 30)
            )


            cv2.circle(
                frame,
                (
                    int(self.x),
                    int(self.y)
                ),
                radius,
                self.color,
                -1
            )



def create_particles(
        x,
        y,
        color,
        count=20,power=5
):

    for i in range(count):

        particles.append(
            Particle(
                x,
                y,
                color,power
            )
        )



def update_particles(canvas):

    for p in particles[:]:

        p.update()

        p.draw(canvas)


        if p.life <= 0:

            particles.remove(p)

def create_glow(layer, x, y, radius, color):

    h, w = layer.shape[:2]

    # 扩大影响范围
    radius = int(radius * 1.7)

    yy, xx = np.ogrid[:h, :w]

    distance = np.sqrt(
        (xx - x) ** 2 +
        (yy - y) ** 2
    )

    mask = distance <= radius

    # 渐变
    alpha = 1 - distance / radius
    alpha = np.clip(alpha, 0, 1)




    gradient = np.zeros_like(layer)

    for i in range(3):
        gradient[:, :, i] = color[i]

    strength = 1.5

    layer[mask] = gradient[mask]