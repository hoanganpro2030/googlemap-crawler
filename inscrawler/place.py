class Place:
    name = ""
    comments = 0
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