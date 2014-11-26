from orm import MySQLModel

class MyModel(MySQLModel):
    def __init__(self):
        self.connect("127.0.0.1", 3308, "test", "PASSWORD", "test2")

class flavor(MyModel):
    pass

class color(MyModel):
    pass

class user(MyModel):
    pass
    _has_one = [color()]
    #_has_many_to_many = [flavor()]

x = user()
while x.select("username").select_related("color", ["color"]).get():
    print x.username
x.username = "adamsna"
x.save()
x.color.color = "green"
x.color.save()