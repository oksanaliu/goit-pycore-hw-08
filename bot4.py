import pickle
from datetime import datetime, timedelta
import os

class Field:
    pass

class Name(Field):
    def __init__(self, value):
        self.value = value

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone_number(value):
            raise ValueError("Invalid phone number format. Use format: XXXXXXXXXX")
        self.value = value

    def validate_phone_number(self, number):
        return len(number) == 10 and number.isdigit()

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

class AddressBook:
    def __init__(self):
        self.contacts = []

    def add_contact(self, name, phones=None, birthday=None):
        record = self.find_contact(name)
        if not record:
            record = Record(name)
            self.contacts.append(record)
        if phones:
            for phone in phones:
                record.add_phone(phone)
        if birthday:
            record.add_birthday(birthday)

    def find_contact(self, name):
        for contact in self.contacts:
            if contact.name.value.lower() == name.lower():
                return contact
        return None

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for contact in self.contacts:
            if contact.birthday:
                birthday_date = contact.birthday.value.date()
                next_birthday = datetime(today.year, birthday_date.month, birthday_date.day).date()

                if next_birthday < today:
                    next_birthday = datetime(today.year + 1, birthday_date.month, birthday_date.day).date()

                days_until_birthday = (next_birthday - today).days

                if 0 <= days_until_birthday <= 7:
                    if next_birthday.weekday() >= 5:
                        days_until_birthday += (7 - next_birthday.weekday())
                        next_birthday += timedelta(days=(7 - next_birthday.weekday()))

                    congratulation_date = next_birthday.strftime("%Y.%m.%d")

                    upcoming_birthdays.append({"name": contact.name.value, "congratulation_date": congratulation_date})

        return upcoming_birthdays

    def add_phone_to_contact(self, name, phone):
        contact = self.find_contact(name)
        if contact:
            contact.add_phone(phone)
            print("Phone number successfully added to contact", name)
        else:
            print("Contact with name '{}' not found.".format(name))

def load_contacts():
    file_path = "contacts.pkl"
    if os.path.exists(file_path):
        print(f"Loading contacts from {file_path}")
        try:
            with open(file_path, "rb") as file:
                address_book = pickle.load(file)
                print("Contacts loaded successfully.")
                return address_book
        except (FileNotFoundError, EOFError, pickle.UnpicklingError) as e:
            print(f"Failed to load contacts: {e}")
            return AddressBook()
    else:
        print(f"No existing contacts file found at {file_path}")
        return AddressBook()

def save_contacts(address_book):
    file_path = "contacts.pkl"
    print(f"Saving contacts to {file_path}")
    with open(file_path, "wb") as file:
        pickle.dump(address_book, file)
    print("Contacts saved successfully.")

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            return str(e)
    return inner

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays: {}".format(", ".join([b["name"] for b in upcoming_birthdays]))
    else:
        return "No upcoming birthdays"

if __name__ == "__main__":
    book = load_contacts()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = user_input.split()  # Assuming simple split for command parsing

        if command in ["close", "exit"]:
            print("Good bye!")
            save_contacts(book)
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            name = args[0]
            phones = args[1:]
            book.add_contact(name, phones)
            print(f"Added contact: {name} with phones {phones}")

        elif command == "change":
            name = args[0]
            old_phone = args[1]
            new_phone = args[2]
            contact = book.find_contact(name)
            if contact:
                contact.phones = [Phone(new_phone) if phone.value == old_phone else phone for phone in contact.phones]
                print(f"Changed phone for {name} from {old_phone} to {new_phone}")
            else:
                print(f"No contact found with name {name}")

        elif command == "phone":
            name = args[0]
            contact = book.find_contact(name)
            if contact:
                print(f"{name}'s phones: {[phone.value for phone in contact.phones]}")
            else:
                print(f"No contact found with name {name}")

        elif command == "all":
            for contact in book.contacts:
                phones = ", ".join([phone.value for phone in contact.phones])
                birthday = contact.birthday.value.strftime("%d.%m.%Y") if contact.birthday else "No birthday"
                print(f"Name: {contact.name.value}, Phones: {phones}, Birthday: {birthday}")

        elif command == "add-birthday":
            name = args[0]
            birthday = args[1]
            contact = book.find_contact(name)
            if contact:
                contact.add_birthday(birthday)
                print(f"Added birthday for {name}: {birthday}")
            else:
                print(f"No contact found with name {name}")

        elif command == "show-birthday":
            name = args[0]
            contact = book.find_contact(name)
            if contact and contact.birthday:
                print(f"{name}'s birthday: {contact.birthday.value.strftime('%d.%m.%Y')}")
            else:
                print(f"No birthday found for {name}")

        elif command == "birthdays":
            print(birthdays(args, book))

        elif command == "add-phone":
            if len(args) == 2:
                name, phone = args
                book.add_phone_to_contact(name, phone)
            else:
                print("Invalid command. Usage: add-phone <name> <phone>")

        else:
            print("Invalid command.")