import os
import json
from datetime import datetime
import time
from datetime import date
from typing import Dict,Tuple, Any 
import hashlib

class Atm:
    account_no = 5000000
    
    def __init__(self) -> None:
        '''Initializes the ATM system.

    - Sets the file path for storing user data in JSON format.
    - Loads all existing users from the JSON file into memory.
    - If the file does not exist or is empty, an empty dictionary is initialized.

    This ensures persistent storage of user account data across program runs.'''
        self.file_path = 'data/users.json'
        self.users = self.load_users()
# --------------------------------------------------

    def load_users(self) -> Dict[str, Dict[str, Any]]:
        '''Loads user data from the JSON file.

    Behavior:
    - Creates the 'data' directory if it does not exist.
    - If the JSON file does not exist or is empty, initializes it with an empty dictionary.
    - Reads and returns all user account data as a Python dictionary.

    Returns:
        dict: A dictionary containing all users and their account details.'''
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            with open(self.file_path, 'w') as f:
                json.dump({}, f, indent = 4)
            return {}
        with open(self.file_path, 'r') as f:
            return json.load(f)
    
    def save_users(self) -> None:
        '''Saves the current state of all users to the JSON file.

    This method ensures that:
    - Any modification (deposit, withdraw, transfer, limit change, etc.)
      is permanently stored.
    - Data persistence is maintained between program executions.'''
        
        with open(self.file_path, 'w') as f:
            json.dump(self.users, f, indent = 4)

    def start(self) -> None:
        '''Entry point of the ATM system.

    Displays the main menu:
        1. Create Account
        2. Login

    Continues running until the user exits.
    Routes the user to the appropriate function based on input.'''
        while True:
            service = input(''' 
1. CREATE ACCOUNT
2. LOGIN
3. FORGET PIN
4. EXIT
CHOOSE THE SERVICE... ''')
            if service == '1':
                self.create_account()
            elif service == '2':
                self.login()
            elif service == '3':
                self.forget_pin()
            else:
                print("Thank you for being our customer")
                break        
# ----------------------Creating Accounts----------------------------------------
    def create_account(self) -> None:
        ''' Creates a new bank account.

    Steps:
    - Takes account number as input.
    - Checks if account already exists.
    - If not, collects:
        - Name
        - PIN
        - Initial balance
    - Initializes default daily limits for:
        - Withdraw
        - Deposit
        - Transfer
    - Initializes security attributes:
        - Failed login attempts
        - Lock status
    - Saves the user data to JSON.

    Prevents duplicate account numbers.'''
        self.account_no += 1
        account_no = str(self.account_no)
        answer = input("What is your favourite color: ? ").lower()

        if account_no not in self.users:
            self.users[account_no] = {
            'name' :  input("Enter your name: "),
            'pin' :  self.hash_pin(int(input("Enter your Pin: "))),
            'balance' : float(input("Enter your balance: ")),
            'transactions' : [],
            'transfer_transactions' : [],
            'failed_attempts': 0,
            'is_locked': False,
            'lock_time': None,
            'withdraw_limit' : 20000,
            'deposit_limit' : 20000,
            'transfer_limit' : 10000,
            'security_question' : "What is your favourite color?",
            'security_answer' : answer.lower()
            }
            self.save_users()
            print(f"Account created successfully your ACCOUNT NO: {self.account_no}")
        else:
            print("Account already exists")

    
    def login(self) -> None:
        '''Authenticates a user using account number and PIN.

    Security Features:
    - Checks if account exists.
    - Checks if account is temporarily locked.
    - Locks account for 60 seconds after more than 3 failed attempts.
    - Resets failed attempts after successful login.

    If authentication is successful:
        - Redirects user to the ATM service menu.'''
        account_no = input("Enter the Account no: ")
        if account_no not in self.users:
            print("Account does not exist")
            return 
        user = self.users[account_no]

        #checking for lock account 
        if user['is_locked']:
            current_time = time.time()
            if current_time - user['lock_time'] <= 60:
                print("Account is temporarily locked. Try again later.")
                return
            else:
                user['failed_attempts'] = 0
                user['is_locked'] = False
                user['lock_time'] = None

        pin = self.hash_pin(int(input("Enter your PIN: ")))
        if user and pin == self.users[account_no]['pin']:
            user['failed_attempts'] = 0
            user['is_locked'] = False
            user['lock_time'] = None
            self.save_users()
            print()
            print("Welcome ", self.users[account_no]['name'])
            self.user_menu(account_no)
        else:
            user['failed_attempts'] += 1
            print()
            print("lOGIN FAILED")
            if user['failed_attempts'] > 3:
                user['is_locked'] = True
                user['lock_time'] = time.time()
                print("Account locked for 60 seconds due to multiple failed attempts.")
            self.save_users()
    
    def forget_pin(self) -> None:
        account_no = input("Enter your account no: ")
        if account_no not in self.users:
            print("Account does not exist")
            return  
        print(self.users[account_no]['security_question'])
        answer = input("Enter your answer: ").lower()
        if answer == self.users[account_no]['security_answer']:
            new_pin = int(input("Enter your new PIN: "))
            self.users[account_no]['pin'] = self.hash_pin(new_pin)
            self.save_users()
            print("PIN has been reset successfully")
        else:
            print("Wrong answer. Cannot reset PIN.")
            
# --------------Customer Menu function
    def user_menu(self,account_no: str) -> None:
        '''Displays the main service menu for a logged-in user.

    Available services:
        1. Check balance
        2. Change PIN
        3. Withdraw money
        4. Deposit money
        5. Transfer money
        6. View transaction history
        7. View transfer history
        8. Change daily limits

    Runs in a loop until the user logs out.'''
        while True:
            user_input = input('''
1. CHECK BALANCE
2. CHANGE PIN
3. WITHDRAW MONEY
4. DEPOSIT MONEY
5. TRANSFER MONEY
6. TRANSACTION HISTORY
7. TRANSFER HISTORY
8. CHANGE DAILY LIMIT
9. MINI BANK STATEMENT
SELECT THE SERVICE YOU WANT TO USE: ''')
            if user_input == '1':
                print(f"Balance: {self.users[account_no]['balance']}")
            elif user_input == '2':
                self.change_pin(account_no)
            elif user_input == '3':
                self.withdraw_money(account_no)
            elif user_input == '4':
                self.deposit_money(account_no)
            elif user_input == '5':
                self.transfer_money(account_no)
            elif user_input == '6':
                self.transaction_history(account_no)
            elif user_input == '7':
                self.transfer_history(account_no)
            elif user_input == '8':
                self.change_daily_limit(account_no)
            elif user_input == '9':
                self.mini_statement(account_no)
            else:
                print("Logged out")
                break
    
    def hash_pin(self, pin:int) -> str:
        '''Hashes the provided PIN using a simple algorithm.
    Note:   This is a very basic hashing mechanism and should not be used in production.
    For demonstration purposes only.'''
        return hashlib.sha256(str(pin).encode()).hexdigest()
          # Simple hash for demonstration
    
# -------------CHANGE PIN-------------------------
    def change_pin(self, account_no:str ) -> None:
        '''Allows the user to change their account PIN.

    Process:
    - Verifies old PIN.
    - If correct, updates to new PIN.
    - Saves updated data to JSON.

    Ensures only authorized PIN changes.'''
        if self.users[account_no]['pin'] == self.hash_pin(int(input("Enter old PIN: "))):
            self.users[account_no]['pin'] = self.hash_pin(int(input("Enter new PIN: ")))
            self.save_users()
            print()
            print("PIN has been changed successfully")
        else:
            print("Wrong PIN")
    
    def withdraw_money(self, account_no:str ) -> None:
        ''' Handles money withdrawal from the account.

    Validation Steps:
    - Verifies PIN.
    - Checks daily withdrawal limit.
    - Ensures withdrawal does not exceed:
        - Available account balance
        - User's daily withdrawal limit

    If valid:
        - Deducts amount from balance.
        - Records transaction with timestamp.
        - Updates remaining daily limit.
        - Saves changes to JSON.

    Prevents overdraft and limit violation.'''
        if self.users[account_no]['pin'] == self.hash_pin(int(input("Enter your PIN: "))):
            amount = float(input("Enter the amount: "))
            user = self.users[account_no]
            # Get today's total withdrawal
            total_withdraw_today = self.calculate_today_withdraw_deposit(account_no)[0]
            daily_limit = user['withdraw_limit']
            # Check if daily limit exists
            if daily_limit is None:
                daily_limit = 50000  # default system limit
            if total_withdraw_today + amount > daily_limit:
                remaining_limit = daily_limit - total_withdraw_today
                print()
                print(f"Daily withdrawal limit exceeded!")
                print(f"You can withdraw only {remaining_limit} more today.")
                return
            # Check balance
            if amount > user['balance']:
                print("Insufficient Balance")
                return
            # Process withdrawal
            user['balance'] -= amount
            user['transactions'].append({
                'type': 'withdraw',
                'amount': amount,
                'timestamp': str(datetime.now())
            })
            self.save_users()
            print()
            print(f"{amount} has been withdrawn successfully")
            print(f"Remaining Daily Limit: {daily_limit - (total_withdraw_today + amount)}")
        else:
            print("Wrong PIN")

    def deposit_money(self, account_no: str) -> None:
        '''Handles depositing money into the account.

    Validation Steps:
    - Verifies PIN.
    - Checks daily deposit limit.
    - Ensures deposit does not exceed allowed daily limit.

    If valid:
        - Adds amount to account balance.
        - Records deposit transaction with timestamp.
        - Updates remaining daily deposit limit.
        - Saves changes to JSON.'''
        if self.users[account_no]['pin'] == self.hash_pin(int(input("Enter your PIN: "))):
            amount = float(input("Enter the amount: "))
            user = self.users[account_no]
            # Get today's total withdrawal
            total_deposit_today = self.calculate_today_withdraw_deposit(account_no)[1]
            daily_limit = user['deposit_limit']
            # Check if daily limit exists
            if daily_limit is None:
                daily_limit = 50000  # default system limit
            if total_deposit_today + amount > daily_limit:
                remaining_limit = daily_limit - total_deposit_today
                print()
                print(f"Daily withdrawal limit exceeded!")
                print(f"You can deposit only {remaining_limit} more today.")
                return
            # Check balance
            if amount > user['balance']:
                print("Insufficient Balance")
                return
            # Process withdrawal
            user['balance'] += amount
            user['transactions'].append({
                'type': 'deposit',
                'amount': amount,
                'timestamp': str(datetime.now())
            })
            self.save_users()
            print()
            print(f"{amount} has been deposit successfully")
            print(f"Remaining Daily Limit: {daily_limit - (total_deposit_today + amount)}")
        else:
            print("Wrong PIN")

    def transaction_history(self, account_no: str) -> None:
        ''' Displays all withdrawal and deposit transactions
    for the specified account.

    Shows:
        - Transaction type (withdraw/deposit)
        - Amount
        - Timestamp

    If no transactions exist, informs the user.'''
        if not self.users[account_no]['transactions']:
            print("No transactions yet")
        else:
            for transaction in self.users[account_no]['transactions']:
                print(transaction)

    def transfer_money(self, account_no: str) -> None:
        '''Transfers money from the current account to another account.

    Validation Steps:
    - Ensures receiver account exists.
    - Prevents transferring to the same account.
    - Checks daily transfer limit.
    - Ensures sufficient balance.

    If valid:
        - Deducts amount from sender.
        - Adds amount to receiver.
        - Records transaction for both accounts.
        - Stores timestamp and account holder name.
        - Saves changes to JSON.'''
        receiver_account_no = input("Enter the receiver ACCOUNT NO: ")
        if receiver_account_no == account_no:
            print("Please enter a different account no....")
        else:
            if receiver_account_no in self.users:
                amount = float(input("Enter the amount to transfer: "))
                user = self.users[account_no]
                total_transfer_today = self.calculate_today_transfer(account_no)
                daily_transfer_limit = user['transfer_limit']

                if daily_transfer_limit is None:
                    daily_transfer_limit = 50000

                if total_transfer_today + amount > daily_transfer_limit:
                    remaining_transfer_limit = daily_transfer_limit - total_transfer_today
                    print()
                    print(f"Daily Transfer Limit exceed!")
                    print(f"You can transfer only {remaining_transfer_limit}")
                else:
                    if amount <= self.users[account_no]['balance']:
                        self.users[account_no]['balance'] -= amount
                        self.users[account_no]['transfer_transactions'].append({
                            'type' : 'SEND', 
                            'receiver_account_no': receiver_account_no,
                            'amount' : amount,
                            'timestamp': str(datetime.now()),
                            'name_of_account_holder' : self.users[receiver_account_no]['name']
                        })
                        self.users[receiver_account_no]['balance'] += amount
                        self.users[receiver_account_no]['transfer_transactions'].append({
                            'type' : 'RECEIVED',
                            'sender_account_no' : account_no,
                            'amount' :  amount,
                            'timestamp': str(datetime.now()),
                            'name_of_account_holder' : self.users[account_no]['name']
                        })
                        self.save_users()
                        print()
                        print(F"YOU SENT {amount} ruppes TO {receiver_account_no}")
                        print()
                        print(f"YOUR CURRENT BALANCE: {self.users[account_no]['balance']}")
                    else:
                        print("INSUFFICIENT BALANCE TO TRANSFER MONEY")
            else:
                print("PLEASE ENTER A VALID ACCOUNT NUMBER!")

    def calculate_today_withdraw_deposit(self, account_no: str) -> Tuple[float, float]:
        '''Calculates today's total withdrawal and deposit amounts.

    Logic:
    - Iterates through all transactions.
    - Filters transactions with today's date.
    - Separates totals for:
        - Withdraw
        - Deposit

    Returns:
        tuple:
            (total_withdraw_today, total_deposit_today)'''
        transactions = self.users[account_no]['transactions']
        today = str(date.today())  # format: YYYY-MM-DD
        total_withdraw_today = 0
        total_deposit_today = 0
        for transaction in transactions:
            transaction_date = transaction["timestamp"].split()[0]
            if transaction["type"] == "withdraw" and transaction_date == today:
                total_withdraw_today += transaction["amount"]
            if transaction["type"] == "deposit" and transaction_date == today:
                total_deposit_today += transaction["amount"]
        return total_withdraw_today , total_deposit_today
    
    def calculate_today_transfer(self, account_no: str) -> float:
        '''Calculates total money sent today from the account.

    Logic:
    - Iterates through transfer transactions.
    - Filters only 'SEND' type transfers for today's date.
    - Sums the total transferred amount.

    Returns:
        float: Total amount transferred today.'''
        transfer_transactions = self.users[account_no]['transfer_transactions']
        today = str(date.today())
        total_send_money = 0
        for transfer in transfer_transactions:
            transfer_date = transfer["timestamp"].split()[0]
            if transfer["type"] == "SEND" and transfer_date == today:
                total_send_money += transfer["amount"]
        return total_send_money

    def transfer_history(self, account_no: str) -> None:
        ''' Displays all transfer transactions related to the account.

    Includes:
        - Sent transactions
        - Received transactions
        - Amount
        - Timestamp
        - Other party account details

    If no transfers exist, informs the user.'''
        if not self.users[account_no]['transfer_transactions']:
            print("No Transfers yet to any account!")
        else:
            for transfer in self.users[account_no]['transfer_transactions']:
                print(transfer)
    
    def change_daily_limit(self, account_no: str) -> None:
        '''Allows the user to increase daily transaction limits.

    Options:
        - Withdraw limit
        - Deposit limit

    Based on selected multiplier (20, 30, 80):
        - Multiplies the current limit accordingly.

    Saves updated limits to JSON.

    Note:
        This method modifies only withdraw and deposit limits.
        Transfer limit remains unchanged.'''
        choice = input("Which limit you want to increase(withdraw/deposit/transfer): ").lower()
        if choice in ['w', 'withdraw']:
            limit_value = int(input("Choose the increased limit_value you want(20, 30, 80): "))
            if limit_value == 20:
                self.users[account_no]['withdraw_limit'] *= 2
            elif limit_value == 30:
                self.users[account_no]['withdraw_limit'] *= 3
            else:
                self.users[account_no]['withdraw_limit'] *= 8
            self.save_users()
            print(f"Withdraw limit has been increased to {self.users[account_no]['withdraw_limit']}")

        elif choice in ['d', 'deposit']:
            limit_value = int(input("Choose the increased limit you want(20, 30, 80): "))
            if limit_value == 20:
                self.users[account_no]['deposit_limit'] *= 2
            elif limit_value == 30:
                self.users[account_no]['deposit_limit'] *= 3
            else:
                self.users[account_no]['deposit_limit'] *= 8
            self.save_users()
            print(f"Deposit limit has been increased to {self.users[account_no]['deposit_limit']}")
        
        elif choice in ['t', 'transfer']:
            limit_value = int(input("Choose the increased limit you want(20, 30, 80): "))
            if limit_value == 20:
                self.users[account_no]['transfer_limit'] *= 2
            elif limit_value == 30: 
                self.users[account_no]['transfer_limit'] *= 3
            else:                
                self.users[account_no]['transfer_limit'] *= 8
            self.save_users()   
            print(f"Transfer limit has been increased to {self.users[account_no]['transfer_limit']}")
        else:
            print("Invalid choice. Please choose either 'withdraw', 'deposit' or 'transfer'.")  

    def mini_statement(self, account_no):
        ''' Displays transaction statement between a given date range.

    User inputs:
        - Start date (YYYY-MM-DD)
        - End date (YYYY-MM-DD)

    Filters transactions within the date range and prints:
        - Type (withdraw/deposit)
        - Amount
        - Timestamp

    Also calculates:
        - Total deposited
        - Total withdrawn'''
        
        try:
            start_date = datetime.strptime(input("Enter start date (YYYY-MM-DD): "), "%Y-%m-%d").date()
            end_date = datetime.strptime(input("Enter end date (YYYY-MM-DD): "), "%Y-%m-%d").date()

        except ValueError:
            print("Invalid date format. please use (YYYY-MM-DD) ")
        transactions = self.users[account_no]['transactions']
        transfer_transactions = self.users[account_no]['transfer_transactions']

        if not transactions:
            print("No Transactions yet")
            return
        if not transfer_transactions:
            print("No Transfers yet")

        print("\n==========MINI BANK STATEMENT============")
        total_deposit = 0.0
        total_withdraw = 0.0
        total_send = 0.0
        total_receive = 0.0
        found = False

        for transaction in transactions:
            transaction_date = datetime.strptime(transaction['timestamp'].split()[0],"%Y-%m-%d").date()
            if start_date <= transaction_date <= end_date: 
                found = True
                print(f"{transaction['type'].upper()} | "
                      f"{transaction['amount']} | "
                      f"{transaction_date}")

                if transaction['type'] == 'withdraw':
                    total_withdraw += transaction['amount']
                elif transaction['type'] == 'deposit':
                    total_deposit += transaction['amount']
        print()
        for transfer in transfer_transactions:
            transfer_date = datetime.strptime(transfer['timestamp'].split()[0], "%Y-%m-%d").date()
            if start_date <=  transfer_date <= end_date:
                found = True
                print(f"{transfer['type']} | "
                      f"{transfer['amount']} | "
                      f"{transfer_date}")
                
                if transfer['type'] == 'SEND':
                    total_send  += transfer['amount']
                elif transfer['type'] == 'RECEIVED':
                    total_receive += transfer['amount']

        if not found:
            print("No transactions found over the period")
        
        print("**********SUMMARY**********")
        print(F"TOTAL DEPOSITED {total_deposit}")
        print(F"TOTAL WITHDRAWN: {total_withdraw}")
        print(f"NET AMOUNT : {total_deposit - total_withdraw}")
        print()
        print(f"TOTAL SEND: {total_send}")
        print(F"TOTAL RECEIVED: {total_receive}")
        print(f"NET TRANSFER AMOUNT: {total_receive-total_send}")
