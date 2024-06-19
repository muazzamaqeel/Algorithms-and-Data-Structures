#include <iostream>
#include <string>

using namespace std;

// Forward declarations
class Invoice;
class PaymentMethod;
class Service;

// Room class
class Room {
    int number;
    string category;
    double price;
    bool isBooked;

public:
    Room(int num, string cat, double pr) : number(num), category(cat), price(pr), isBooked(false) {}

    void bookRoom() { isBooked = true; }
    bool isAvailable() const { return !isBooked; }
    double getPrice() const { return price; }
    string getCategory() const { return category; }
};

// Service class
class Service {
    string name;
    double cost;

public:
    Service(string nm, double cst) : name(nm), cost(cst) {}
    double getServiceCost() const { return cost; }
    string getName() const { return name; }
};

// PaymentMethod abstract class
class PaymentMethod {
public:
    virtual void pay(double amount) = 0;
};

// CreditCard class
class CreditCard : public PaymentMethod {
public:
    void pay(double amount) override {
        cout << "Paid " << amount << " using Credit Card." << endl;
    }
};

// Cash class
class Cash : public PaymentMethod {
public:
    void pay(double amount) override {
        cout << "Paid " << amount << " using Cash." << endl;
    }
};

// Invoice class
class Invoice {
    double amount;
    Service services[10];
    int serviceCount;

public:
    Invoice() : amount(0), serviceCount(0) {}

    void addService(Service service) {
        if (serviceCount < 10) {
            services[serviceCount++] = service;
        }
    }

    double calculateTotal() {
        amount = 0;
        for (int i = 0; i < serviceCount; ++i) {
            amount += services[i].getServiceCost();
        }
        return amount;
    }
};

// Customer class
class Customer {
    string name;
    int id;
    Service services[10];
    int serviceCount;

public:
    Customer(string nm, int id) : name(nm), id(id), serviceCount(0) {}

    void requestService(Service service) {
        if (serviceCount < 10) {
            services[serviceCount++] = service;
        }
    }

    void pay(Invoice invoice, PaymentMethod& method) {
        double amount = invoice.calculateTotal();
        method.pay(amount);
    }

    string getName() const { return name; }
    Service* getServices() { return services; }
    int getServiceCount() const { return serviceCount; }
};

// Hotel class (Facade)
class Hotel {
    Room rooms[10];
    int roomCount;
    Customer customers[10];
    int customerCount;

public:
    Hotel() : roomCount(0), customerCount(0) {}

    void addRoom(Room room) {
        if (roomCount < 10) {
            rooms[roomCount++] = room;
        }
    }

    void addCustomer(Customer customer) {
        if (customerCount < 10) {
            customers[customerCount++] = customer;
        }
    }

    void reserveRoom(Customer& customer, string roomCategory) {
        for (int i = 0; i < roomCount; ++i) {
            if (rooms[i].isAvailable() && rooms[i].getCategory() == roomCategory) {
                rooms[i].bookRoom();
                cout << "Room reserved for customer: " << customer.getName() << endl;
                return;
            }
        }
        cout << "No available room in category: " << roomCategory << endl;
    }

    Invoice generateInvoice(Customer& customer) {
        Invoice invoice;
        Service* services = customer.getServices();
        int serviceCount = customer.getServiceCount();
        for (int i = 0; i < serviceCount; ++i) {
            invoice.addService(services[i]);
        }
        invoice.calculateTotal();
        return invoice;
    }
};
