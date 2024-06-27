import secrets
import string
from faker import Faker
from random_address import random_address


def get_address_detail():
    has_city = False
    while not has_city:
        address = random_address.real_random_address()
        keys = list(address.keys())
        if 'city' in keys:
            return address


class CountryLocale:
    UK = 'en_GB'
    US = 'en_US'
    CA = 'en_CA'
    JP = 'ja_JP'


class CustomGEN:
    def __init__(self, locale=CountryLocale.US):
        self.birthday = None
        self.password = None
        self.zip = None
        self.country = None
        self.city = None
        self.address_title = None
        self.address2 = None
        self.address1 = None
        self.state = None
        self.nickname = None
        self.cvv = None
        self.email = None
        self.cc_expire = None
        self.credit_card = None
        self.phone = None
        self.lastname = None
        self.firstname = None
        self.locale = locale
        self.fake = Faker(self.locale)
        self.customer()

    def customer(self):
        self.firstname = self.fake.first_name()
        self.lastname = self.fake.last_name()
        self.birthday = self.fake.date_of_birth()
        self.phone = '9234567890'
        self.credit_card = "4111111111111111"
        self.cc_expire = self.fake.credit_card_expire()
        self.cvv = '456'
        email = self.fake.email().split('@')
        self.email = email[0] + '123' + ''.join(secrets.choice(string.digits) for i in range(4)) + '@' + email[1]
        self.password = "Test123#"
        self.nickname = self.firstname + ''.join(
            secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(7))
        self.address_title = self.nickname

        if self.locale == CountryLocale.US:
            address = get_address_detail()
            self.address1 = address["address1"]
            self.address2 = "".join(c for c in address["address2"] if c.isalnum())
            self.city = address["city"]
            self.state = address["state"]
            self.country = 'United States'
            self.zip = address["postalCode"]
        elif self.locale == CountryLocale.CA:
            self.address1 = self.fake.street_address()
            self.address2 = "".join(c for c in self.fake.secondary_address() if c.isalnum())
            self.city = self.fake.city()
            self.state = self.fake.province_abbr()
            self.country = self.fake.current_country()
            self.zip = self.fake.postcode()
        elif self.locale == CountryLocale.JP:
            self.address1 = self.fake.street_address()
            self.address2 = self.fake.building_name()
            self.city = self.fake.city()
            self.state = self.fake.prefecture()
            self.country = self.fake.current_country()
            self.zip = self.fake.postcode()
        else:
            self.address1 = self.fake.street_address()
            self.address2 = "".join(c for c in self.fake.secondary_address() if c.isalnum())
            self.city = self.fake.city()
            self.country = self.fake.current_country()
            self.zip = self.fake.postcode()

    def print_customer_info(self):
        print(self.firstname + " " + self.lastname)
        print(self.email)
        print(self.birthday)
        if self.locale == CountryLocale.US or self.locale == CountryLocale.CA:
            print(
                self.address1 + "\n" + self.address2 + "\n" + self.city + "\n" + 'state=' + self.state + "\n" + self.zip
                + "\n" + self.country)
        else:
            print(self.address1 + "\n" + self.address2 + "\n" + self.city + "\n" + self.zip + "\n" + self.country)


# ashish = CustomGEN()
# ashish.print_customer_info()
