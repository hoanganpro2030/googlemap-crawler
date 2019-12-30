class Place:
    name = ""
    comments = 0
    comments_s = 0      #1.0-0.8
    comments_a = 0      #0.8-0.6
    comments_b = 0      #0.6-0.4
    comments_c = 0      #0.4-0.2
    comments_d = 0      #0.2-0.0
    comments_e = 0      #0.0 - -0.2
    comments_f = 0      #-0.2 - -0.4
    comments_g = 0      #-0.4 - -0.6
    comments_h = 0      #-0.6 - -0.8
    comments_i = 0      #-0.8 - -1.0
    stars = 0
    star1s = 0
    star2s = 0
    star3s = 0
    star4s = 0
    star5s = 0

    def __init__(self):
        pass

    def update_star(self, n):
        if n == 1:
            self.star1s += 1
        elif n == 2:
            self.star2s += 1
        elif n == 3:
            self.star3s += 1
        elif n == 4:
            self.star4s += 1
        elif n == 5:
            self.star5s += 1

    def update_comments(self, n):
        if n >= 0.8 and n <=1.0:
            self.comments_s += 1
        if n >= 0.6 and n < 0.8:
            self.comments_a += 1
        if n >= 0.4 and n < 0.6:
            self.comments_b += 1
        if n >= 0.2 and n < 0.4:
            self.comments_c += 1
        if n >= 0.0 and n < 0.2:
            self.comments_d += 1
        if n >= -0.2 and n < 0.0:
            self.comments_e += 1
        if n >= -0.4 and n < -0.2:
            self.comments_f += 1
        if n >= -0.6 and n < -0.4:
            self.comments_g += 1
        if n >= -0.8 and n < -0.6:
            self.comments_h += 1
        if n >= -1.0 and n < -0.8:
            self.comments_i += 1