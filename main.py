#Grocery Store BUY'n GO System
#LOMOYA
#ONES
#ABOLOC 
#SORISO

import csv
from abc import ABC, abstractmethod

class Grocery_System(ABC):
    def __init__(self):
        self.grocery_list = {}
        self.customer_list = {}
        self.cart = {}
#============================================LOAD GROCERY LIST================================================================
    def load_grocery_list(self, filename="grocery_list.csv"):
        try:
            with open(filename, 'r', newline='') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row:
                        number = int(row[0])
                        name = row[1]
                        quantity = int(row[2])
                        unit = row[3]
                        price = float(row[4])
                        product = Product(number, name, quantity, unit, price)
                        self.grocery_list[number] = product
        except FileNotFoundError:
            print(f"'{filename}' not found. Starting with an empty grocery list.")
            
  #===========================================SAVE CUSTOMER ORDERS================================================================          

    def save_customer_orders_to_csv(self, filename="customer_orders.csv"):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            for customer, orders in self.cart.items():
                for item in orders:
                    product_name = item[0]
                    quantity = item[1]
                    unit = item[2]
                    price = item[3]
                    writer.writerow([customer, product_name, quantity, unit, price])

    @abstractmethod
    def processing_order(self, order):
        pass

#============================================CLASS PRODUCT================================================================

class Product:
    def __init__(self, number, name, quantity, unit, price):
        self._number = number
        self._name = name
        self._quantity = quantity
        self._unit = unit
        self._price = price

    def get_display_details(self):
        return [self._number, self._name, self._quantity, self._unit, self._price]

    def update_quantity(self, quantity):
        self._quantity = quantity

#============================================CLASS USER================================================================
class User(Grocery_System):
    def __init__(self, name, balance):
        super().__init__()
        self._name = name
        self._balance = balance
        self._cart = []
 #============================================ADDING CART================================================================
    def adding_cart(self, product, quantity):
        if product._quantity >= quantity:
            total_price = product._price * quantity
            self._cart.append([product._name, quantity, product._unit, total_price])
            # Reduce stock after adding to cart
            product.update_quantity(product._quantity - quantity)
            return True
        else:
            return False
#============================================CHECK OUT================================================================
    def checkout(self):
        if not self._cart:
            return None, 0  # signal that cart is empty
        total = sum(item[3] for item in self._cart)
        if total <= self._balance:
            self._balance -= total
            return True, total
        else:
            return False, total


#============================================CLASS CUSTOMER================================================================
class Customer(User):
    def __init__(self, name, balance):
        super().__init__(name, balance)

#============================================VIEW CART================================================================
    def view_cart(self):
        print("=" * 34)
        print("Your Cart:")
        if not self._cart:
            print("Your cart is empty.")
        else:
            for item in self._cart:
                print(f"{item[0]} {item[1]}x {item[2]} - ₱{item[3]:.2f}")
            print(f"Total - ₱{sum(item[3] for item in self._cart):.2f}")


#============================================PROCESSING ORDER================================================================
    def processing_order(self, order):
        print("Processing customer order:", order)
        return True

#============================================GROCERY STORE SYSTEM================================================================
class GroceryStoreSystem:
    def __init__(self):
        self.customers = {}
        self.cart = {}

#============================================MAIN MENU================================================================
    def main(self):
        while True:
            print("=" * 34)
            print("  Grocery Store BUY'n GO System")
            print("=" * 34)
            print("1. Customer")
            print("2. Exit")
            print("-" * 34)
            try:
                choice = int(input("Choose a number: "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if choice == 1:
                name = input("Enter your name: ").capitalize()
                try:
                    balance = float(input("Enter your budget: "))
                except ValueError:
                    print("Invalid budget.")
                    continue
                customer = Customer(name, balance)
                customer.load_grocery_list()
                self.customers[name] = customer
                self.customer_menu(customer)
            elif choice == 2:
                print("Exiting the program. Thank you!")
                break
            else:
                print("Invalid input, please try again.")

#============================================CUSTOMER MENU================================================================
    def customer_menu(self, customer):
        while True:
            print("=" * 34)
            print(f"Customer: {customer._name}")
            print(f"Balance: ₱{customer._balance:.2f}")
            print("-" * 34)
            print("               MENU     ")
            print("-" * 34)
            print("1. View Products")
            print("2. View Cart")
            print("3. Checkout")
            print("4. Remove Products from Cart")
            print("5. Exit")
            print("-" * 34)
            choice = input("Choose an option: ")

            if choice == "1":
                self.view_products(customer)
                print("-" * 34)
                print("Would you like to add products?")
                print("-" * 34)
                while True:
                    try:
                        num = int(input("Enter a product code (0 to exit): "))
                        if num == 0:
                            break
                        if not (100 <= num <= 999):
                            print("Invalid product code! Use 3-digit codes.")
                            continue
                        if num in customer.grocery_list:
                            product = customer.grocery_list[num]
                            quantity = int(input(f"Enter a product quantity of '{product._name}' to add: "))
                            if quantity <= 0:
                                print("Quantity must be positive.")
                                continue
                            added = customer.adding_cart(product, quantity)
                            if added:
                                print(f"{product._name} x{quantity} added to cart.")
                            else:
                                print("Insufficient stock!")
                        else:
                            print("Product code not found.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")

            elif choice == "2":
                customer.view_cart()
            elif choice == "3":
                success, total = customer.checkout()
                if success is True:
                    print(f"Checkout successful! Total: ₱{total:.2f}")
                    self.cart[customer._name] = customer._cart.copy()
                    customer.save_customer_orders_to_csv()
                    customer._cart.clear()
                elif success is False:
                    print(f"Insufficient balance. Total: ₱{total:.2f}")
                elif success is None:
                    print("No items in your cart.")

            elif choice == "4":
                self.remove_from_cart(customer)
            elif choice == "5":
                print("Thank you!")
                break
            else:
                print("Invalid choice.")


#============================================VIEW PRODUCTS================================================================
    def view_products(self, customer):
        print("=" * 58)
        print(f"{'Code':<8} {'Product':<15} {'Quantity':<10}    {'Unit':<10} {'Price':<10}")
        for item, product in customer.grocery_list.items():
            details = product.get_display_details()
            stock_status = " [OUT OF STOCK]" if details[2] == 0 else ""
            print(f"{details[0]:<8} {details[1]:<15}    {details[2]:<10} {details[3]:<10} ₱{details[4]:<9.2f}{stock_status}")
        print("=" * 58)

#============================================REMOVE FROM CART================================================================

    def remove_from_cart(self, customer):
        if not customer._cart:
            print("Your cart is empty.")
            return

        print("=" * 34)
        print("Remove an item from your cart:")
        for i, item in enumerate(customer._cart, start=1):
            print(f"{i}. {item[0]} x{item[1]} {item[2]} - ₱{item[3]:.2f}")

        try:
            index = int(input("Enter item number to remove (0 to cancel): "))
            if index == 0:
                print("Cancelled.")
                return
            if 1 <= index <= len(customer._cart):
                removed_item = customer._cart.pop(index - 1)
                for product in customer.grocery_list.values():
                    if product._name == removed_item[0]:
                        product._quantity += removed_item[1]
                        break
                print(f"Removed {removed_item[0]} x{removed_item[1]} from cart.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

#============================================MAIN ENTRY POINT(PARA RUN SA CODE)================================================================
if __name__ == "__main__":
    system = GroceryStoreSystem()
    system.main()