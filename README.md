# Denpointment

> **This is a fork.** The application was written by [Uğur Dindar (Tzesh)](https://github.com/Tzesh) and the original lives at [Tzesh/Denpointment](https://github.com/Tzesh/Denpointment). All the credit for the system, its database and its screenshots below goes to the original author. This fork only revises it (see [What changed in this fork](#what-changed-in-this-fork)). The upstream repository has no licence file, so no licence is granted here beyond what GitHub's terms allow for forks.

Fully-working dentist appointment system which is written in Python using Flask web development, powered by Bootstrap, using MySQL to manipulate data. It's based on a statement of work, developed first its own database and then application. Its database has much quite enough good mock data.

## Main page of the system
![Index page](https://imgur.com/t6Hdc5k.png)

# Denpoinment System - Patient Perspective
Denpointment system allows patients to:
1. Register to the system,
2. Use the system after adding address and telephone information,
3. Add chronic disease information if any,
5. Search for an appointment and book appointments after search,
6. Look for past appointments (treatments if patient has been gone to the appointment), upcoming appointments,
7. And of course change their information like email, password, telephone, address, chronic disease information.

## Patient Registration
![Patient registration](https://imgur.com/nV2d6qF.png)

## New User Login
Users have to add address and telephone information to use the system.
![New user page](https://imgur.com/GbLRAnM.png)

## Profile Page
Users can easily change their email, password, address and phone information in the profile page. But there are some restrictions like patients cannot delete their phone and address number if they only have only one.
![Profile page](https://imgur.com/P2Ll0ow.png)
![Restriction example](https://imgur.com/LSTkyX0.png)
![Changing password](https://imgur.com/ozVFdBr.png)
![Adding address information](https://imgur.com/xNerPop.png)
![Activating account](https://imgur.com/lkJy5bj.png)
## Patient Login
![Patient login page](https://imgur.com/mCYRMmo.png)

## Booking An Appointment
![Booking an appointment](https://imgur.com/7B8tVOj.png)

## My Appointments Page
![My appointments page](https://imgur.com/aJxer79.png)

# Denpoinment System - Dentist Perspective
Denpointment system allows dentists to:
1. See the upcoming appointments,
2. Look for every single patient's profile and see their handy information,
3. Look for today's appointments and add treatment information to them,
4. Look for past treatments (and appointments if patient didn't come to the treatment), and search for past treatments by date,
5. Add holiday information, and of course to view upcoming and past holidays,
6. Look for interesting statistics in the system, that can be either dentist statistics or patient statistics.

## Dentist Login
![Dentist Login](https://imgur.com/YbPIKcC.png)

## Upcoming Appointments
![Upcoming appointments](https://imgur.com/bHQpG6r.png)

## Today's Appointments
![Today's appointments](https://imgur.com/hQJqB7e.png)
![Today's appointments-2](https://imgur.com/Rz4D3nm.png)
![Adding treatment](https://imgur.com/84H1afl.png)
### Note: Dentists can only add treatments (or medicines) to appointments which only booked for today.
![Medicines](https://imgur.com/s1jZQ2A.png)

## Past Treatments
![Past treatments](https://imgur.com/fxjdYEf.png)
![Searching treatments](https://imgur.com/OdvMrZy.png)

## Holidays
![Holidays](https://imgur.com/jfNp0M6.png)
![Adding holiday](https://imgur.com/5iT12sA.png)

## Patient profiles
![Patient profile](https://imgur.com/5hT2d2k.png)

## Patient & Dentist Statistics
![Patient statistics](https://imgur.com/6CA082x.png)
![Dentist statistics](https://imgur.com/z3JeWbw.png)

## How to use Denpointment?
You need Python 3 and a MySQL (or MariaDB) server.

1. Create a database named `dentist_management_system` and import `dentist_management_system.sql` into it.
2. Create a virtual environment and install the packages:
   ```
   python3 -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```
   `Flask-MySQLdb` builds the `mysqlclient` package, which needs the MySQL client library on your machine.
3. Set the database settings and a secret key (all optional, the defaults are shown):
   ```
   export DENPOINTMENT_DB_HOST=localhost
   export DENPOINTMENT_DB_USER=root
   export DENPOINTMENT_DB_PASSWORD=
   export DENPOINTMENT_DB_NAME=dentist_management_system
   export DENPOINTMENT_SECRET_KEY=<a long random string>
   ```
   Without a secret key a random one is made at start, so everybody is logged out whenever the server restarts.
4. Run `.venv/bin/python denpointment.py`. The system runs on http://127.0.0.1:5000/.

![Running denpointment.py](https://imgur.com/UvlNwx7.png)

### Demo credentials
These come with the sample database. The password for all three is `tzesh`.

| Role | Email |
| --- | --- |
| Person | demoperson@gmail.com |
| Patient | demopatient@gmail.com |
| Dentist | demodentist@gmail.com |

## What changed in this fork
- The database settings and the secret key are read from environment variables instead of being written in the code.
- `requirements.txt` lists the packages, `.gitignore` covers the virtual environment, and the README explains the setup step by step.
- `version.py` holds the version of this fork, raised by a git hook on every commit (`Scripts/bump_version.py`; enable it with `git config core.hooksPath .githooks`).

Not tested: this fork has not been run against a MySQL server. The changes only touch configuration and documentation, and the Python files were checked for syntax errors only.
