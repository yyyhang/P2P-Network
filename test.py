class Person(object):
    def __init__(self, name, age, office_area_code, office_number):
        self.name = name
        self.age = age
        self.phone_number = PhoneNumber(office_area_code, office_number)

    def get_phone_number(self):
        return self.phone_number.get_number()

class PhoneNumber(object):
    def __init__(self, area_code ,number):
        self.area_code = area_code
        self.number = number
    def get_number(self):
        return "%s-%s" % (self.area_code, self.number)

test = Person('James',18,'0022','121')
print(test.get_phone_number())
