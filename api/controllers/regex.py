import re


class UsernameInvalid(Exception):
    message = "Username just contains letters, numbers and underscores. It must be at least 3 characters long."
    pass


class EmailInvalid(Exception):
    message = "Email is invalid."
    pass


class PhoneInvalid(Exception):
    message = "Phone is invalid."
    pass


class NameInvalid(Exception):
    message = "Name is invalid."
    pass


class PasswordInvalid(Exception):
    message = "Password must be at least 6 characters long and just contains letters, numbers and one of the following symbols: !@#$%^&*()_+"
    pass


def regex_username(username):
    # min 5 characters
    if re.match(r"^[a-zA-Z0-9_]{3,}$", username):
        return username
        return username
    raise UsernameInvalid


def regex_email(email):
    if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return email
    raise EmailInvalid


def regex_phone(phone_number):
    if re.match(r"^0\d{9}$", phone_number):
        return phone_number
    raise PhoneInvalid


def regex_name(name):
    words = name.split()
    name = ""
    for word in words:
        if not re.match(r"^[a-zA-Z0-9áàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ_]+$", word):
            raise NameInvalid
        name += word.capitalize() + " "
    return name[:-1]


def regex_password(password):
    if re.match(r"^[a-zA-Z0-9!@#$%^&*()_+]{6,}$", password):
        return password
    raise PasswordInvalid

