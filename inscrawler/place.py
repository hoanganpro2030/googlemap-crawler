from mongoengine import *


class Place(Document):
    place_id = StringField(required=True, unique=True)
    name = StringField(required=True)
    address = StringField(required=True)
    location = DictField(required=True)
    comment_list = ListField(DictField())

    reviewer_quant = IntField(required=True, default=0)
    comments = IntField(required=True, default=0)
    comments_s = IntField(required=True, default=0)      #1.0-0.8
    comments_a = IntField(required=True, default=0)      #0.8-0.6
    comments_b = IntField(required=True, default=0)      #0.6-0.4
    comments_c = IntField(required=True, default=0)      #0.4-0.2
    comments_d = IntField(required=True, default=0)      #0.2-0.0
    comments_e = IntField(required=True, default=0)      #0.0 - -0.2
    comments_f = IntField(required=True, default=0)      #-0.2 - -0.4
    comments_g = IntField(required=True, default=0)      #-0.4 - -0.6
    comments_h = IntField(required=True, default=0)      #-0.6 - -0.8
    comments_i = IntField(required=True, default=0)      #-0.8 - -1.0
    stars = FloatField(required=True, default=0.0)
    star1s = IntField(required=True, default=0)
    star2s = IntField(required=True, default=0)
    star3s = IntField(required=True, default=0)
    star4s = IntField(required=True, default=0)
    star5s = IntField(required=True, default=0)

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