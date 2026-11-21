-- Denpointment schema for SQLite (used by the demo mode and the tests).
-- The MySQL version, with its sample data, is dentist_management_system.sql.
PRAGMA foreign_keys = ON;

CREATE TABLE persons (
  ssn        TEXT PRIMARY KEY,
  email      TEXT NOT NULL UNIQUE,
  password   TEXT NOT NULL,
  first_name TEXT NOT NULL,
  last_name  TEXT NOT NULL,
  gender     TEXT NOT NULL CHECK (gender IN ('male', 'female')),
  birth_date date
);

CREATE TABLE addresses (
  address_id INTEGER PRIMARY KEY AUTOINCREMENT,
  p_ssn      TEXT NOT NULL REFERENCES persons (ssn),
  city       TEXT NOT NULL,
  street     TEXT NOT NULL,
  zip_code   TEXT NOT NULL
);

CREATE TABLE person_contact_numbers (
  contact_number TEXT NOT NULL,
  contact_ssn    TEXT NOT NULL REFERENCES persons (ssn),
  PRIMARY KEY (contact_number, contact_ssn)
);

CREATE TABLE chronic_diseases (
  chronic_disease TEXT NOT NULL,
  chronic_ssn     TEXT NOT NULL REFERENCES persons (ssn),
  PRIMARY KEY (chronic_disease, chronic_ssn)
);

CREATE TABLE patients (
  patient_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_ssn TEXT NOT NULL REFERENCES persons (ssn)
);

CREATE TABLE dentists (
  dentist_id  INTEGER PRIMARY KEY AUTOINCREMENT,
  dentist_ssn TEXT NOT NULL REFERENCES persons (ssn),
  room_number TEXT NOT NULL
);

CREATE TABLE holiday_dates (
  holiday_id INTEGER PRIMARY KEY AUTOINCREMENT,
  resting_id INTEGER NOT NULL REFERENCES dentists (dentist_id),
  reason     TEXT,
  rest_date  date NOT NULL
);

CREATE TABLE appointments (
  appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
  d_id  INTEGER NOT NULL REFERENCES dentists (dentist_id),
  p_id  INTEGER NOT NULL REFERENCES patients (patient_id),
  room  TEXT NOT NULL,
  hour  INTEGER NOT NULL,
  month INTEGER NOT NULL,
  day   INTEGER NOT NULL,
  year  INTEGER NOT NULL
);

CREATE TABLE treatments (
  treatment_id INTEGER PRIMARY KEY AUTOINCREMENT,
  description  TEXT,
  charge       INTEGER NOT NULL,
  action       TEXT NOT NULL,
  complaint    TEXT NOT NULL,
  a_id         INTEGER NOT NULL REFERENCES appointments (appointment_id),
  treator_id   INTEGER NOT NULL REFERENCES dentists (dentist_id)
);

CREATE TABLE medicines (
  medicine_id   INTEGER PRIMARY KEY AUTOINCREMENT,
  t_id          INTEGER NOT NULL REFERENCES treatments (treatment_id),
  medicine_name TEXT NOT NULL
);
