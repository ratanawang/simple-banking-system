# Write your code here
import random as r
import sqlite3

conn = sqlite3.connect("card.s3db")
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS card (
        id INTEGER,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
    );
""")
conn.commit()

logged_in = False
# accounts = {}
# balance = 0
current_acc = ""


def print_menu():
    if not logged_in:
        print("1. Create an account")
        print("2. Log into account")
        print("0. Exit")
    else:
        print("1. Balance")
        print("2. Add income")
        print("3. Do transfer")
        print("4. Close account")
        print("5. Log out")
        print("0. Exit")
    selection = input()
    print()
    select(selection)


def select(selection):
    if not logged_in:
        if selection == "1":
            create_account()
        elif selection == "2":
            log_in()
    elif logged_in:
        if selection == "1":
            show_balance()
        elif selection == "2":
            add_income()
        elif selection == "3":
            do_transfer()
        elif selection == "4":
            close_account()
        elif selection == "5":
            log_out()
    if selection == "0":
        exit_program()
    print_menu()


def create_account():
    account_id = str(r.randrange(1000000000))
    account_id = "0" * (9 - len(account_id)) + account_id
    card = "400000" + account_id
    card += create_checksum(card)
    pin = str(r.randrange(10000))
    pin = "0" * (4 - len(pin)) + pin
    # accounts[card] = pin
    print("Your card have been created")
    print("Your card number:")
    print(card)
    print("Your card PIN:")
    print(pin)
    print()
    cur.execute("""INSERT INTO card (number, pin) 
        VALUES ({}, {});""".format(card, pin))
    conn.commit()


def create_checksum(card):
    # using the Luhn algorithm
    temp_card = [int(x) for x in card]
    # double values at odd indices
    for x in range(len(temp_card)):
        if (x + 1) % 2 != 0:
            temp_card[x] *= 2
    # subtract 9 from values over 9
    for y in range(len(temp_card)):
        if temp_card[y] > 9:
            temp_card[y] -= 9
    total = sum(temp_card)
    checksum = 0
    while (total + checksum) % 10 != 0:
        checksum += 1
    return str(checksum)


def log_in():
    global logged_in
    global current_acc
    print("Enter your card number:")
    card = input()
    print("Enter your PIN:")
    pin = input()
    print()
    cur.execute(f"""
        SELECT number, pin
        FROM card
        WHERE (number={card}) AND (pin={pin})
    """)
    if cur.fetchone() is not None:
        # if card in accounts and accounts[card] == pin:
        logged_in = True
        current_acc = card
        print("You have successfully logged in!")
    else:
        print("Wrong card number or PIN!")
    print()


def log_out():
    global logged_in
    logged_in = False
    print("You have successfully logged out!")
    print()


def show_balance():
    cur.execute(f"""
        SELECT balance
        FROM card
        WHERE number={current_acc};
    """)
    # print("Balance: " + str(balance))
    print("Balance: " + cur.fetchone())
    print()


def add_income():
    income = input("Enter income:\n")
    cur.execute(f"""
        UPDATE card
        SET balance = balance + {income}
        WHERE number={current_acc};
    """)
    conn.commit()
    print("Income was added!")
    print()


def do_transfer():
    print("Transfer")
    card_num = input("Enter card number:\n")
    cur.execute(f"""
        SELECT id FROM card WHERE number={card_num};
    """)
    card_exists = cur.fetchone() is not None
    if card_num == current_acc:
        print("You can't transfer money to the same account!")
    elif create_checksum(card_num[:15]) != card_num[-1]:
        print("Probably you made a mistake in the card number. Please try again!")
    elif not card_exists:
        print("Such a card does not exist.")
    else:
        amount = int(input("Enter how much money you want to transfer:\n"))
        cur.execute(f"""
            SELECT balance FROM card WHERE number={current_acc};
        """)
        conn.commit()
        if amount > cur.fetchone()[0]:
            print("Not enough money!")
        else:
            cur.execute(f"""
                UPDATE card
                SET balance = balance - {amount}
                WHERE number={current_acc};
            """)
            conn.commit()
            cur.execute(f"""
                UPDATE card
                SET balance = balance + {amount}
                WHERE number={card_num};
            """)
            conn.commit()
            print("Success!")
    print()


def close_account():
    global logged_in
    cur.execute(f"""
        DELETE FROM card
        WHERE number={current_acc};
    """)
    conn.commit()
    print("The account has been closed!")
    logged_in = False
    print()


def exit_program():
    print("Bye!")
    exit()


print_menu()
