
# SQL-Python-Based GUI – Car Dealership Data Management

This project is a **Python-based database access GUI** tailored for **car dealership data management**.  
It provides a simple interface for managing and querying dealership-related data, connecting to an **Oracle Database** using the **Oracle Instant Client**.

⚠️ **Note**: The Oracle Instant Client is **not included** in this repository due to size constraints.  
Please follow the setup instructions below to install it manually.

---

## Features
- GUI interface built with Python for interacting with dealership data  
- Secure connection to Oracle Database via Oracle Instant Client  
- Supports typical dealership operations such as vehicle inventory and sales records  
- Lightweight, easy to set up using Python virtual environments  

---

##  Prerequisites
Before running the project, ensure you have:

- **Python 3.9+** installed  
- **Oracle Instant Client 23.8 (Basic Package, x64)** installed from Oracle’s official website  
- An Oracle database connection (credentials required)  

---

## 🔧 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/maxpainop/SQL-python-based-GUI.git
cd SQL-python-based-GUI
````
All virtual environment and dependencies are handled already, no need to do anything in that regard.

### 2. Install Oracle Instant Client 23.8

1. Go to the [Oracle Instant Client download page](https://www.oracle.com/database/technologies/instant-client/winx64-64-downloads.html).
2. Download **Instant Client Basic Package – Version 23.8 (64-bit)** for your platform.
3. Unzip the package into a directory (e.g., `C:\oracle\instantclient_23_8`).
4. Add that directory to your system’s **PATH** environment variable.

## Notes

* This program is **dedicated to car dealership management use cases** (inventory, sales, and customer data).
* Oracle Instant Client is required but not bundled due to size & licensing restrictions.
* Database credentials should be stored securely (e.g., environment variables, `.env` files) and not hardcoded.

---

## Contributing

Contributions are welcome, Fork the repo and submit a pull request with improvements or new features.

---

## License

This project is created by Maaz-Maxpainop 


