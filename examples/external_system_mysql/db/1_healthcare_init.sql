-- Create a new schema
CREATE DATABASE IF NOT EXISTS healthcare;

USE healthcare;

-- Table: departments
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: doctors
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department_id INT NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hire_date DATE NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- Table: patients
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    contact_number VARCHAR(15) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: appointments
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date TIMESTAMP NOT NULL,
    reason TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

-- Preload departments data
INSERT INTO departments (name) VALUES
('Cardiology'),
('Neurology'),
('Orthopedics'),
('Pediatrics'),
('General Medicine');

-- Preload doctors data (15 total)
INSERT INTO doctors (name, department_id, email, hire_date) VALUES
('Dr. Alice', 1, 'alice@hospital.com', '2010-03-15'),
('Dr. Bob', 2, 'bob@hospital.com', '2012-07-22'),
('Dr. Charlie', 3, 'charlie@hospital.com', '2008-11-10'),
('Dr. Diana', 4, 'diana@hospital.com', '2015-05-18'),
('Dr. Eve', 5, 'eve@hospital.com', '2011-01-30'),
('Dr. Frank', 1, 'frank@hospital.com', '2014-08-22'),
('Dr. Grace', 2, 'grace@hospital.com', '2016-02-10'),
('Dr. Helen', 3, 'helen@hospital.com', '2017-07-12'),
('Dr. Ian', 4, 'ian@hospital.com', '2018-09-05'),
('Dr. John', 5, 'john@hospital.com', '2019-03-21'),
('Dr. Kelly', 1, 'kelly@hospital.com', '2020-05-11'),
('Dr. Liam', 2, 'liam@hospital.com', '2021-06-15'),
('Dr. Maya', 3, 'maya@hospital.com', '2022-04-19'),
('Dr. Noah', 4, 'noah@hospital.com', '2023-01-20'),
('Dr. Olivia', 5, 'olivia@hospital.com', '2023-07-25');

-- Stored Procedure to Generate Patients
DELIMITER $$

CREATE PROCEDURE GeneratePatients(IN num_patients INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE gender ENUM('Male', 'Female', 'Other');
    WHILE i <= num_patients DO
        SET gender = IF(MOD(i, 3) = 0, 'Other', IF(MOD(i, 2) = 0, 'Female', 'Male'));
        INSERT INTO patients (name, dob, gender, contact_number, email)
        VALUES (
            CONCAT('Patient ', i),
            DATE_ADD('1970-01-01', INTERVAL FLOOR(RAND() * 20000) DAY),
            gender,
            CONCAT('999-888-', LPAD(i, 4, '0')),
            CONCAT('patient', i, '@hospital.com')
        );
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- Call the procedure to generate 100 patients
CALL GeneratePatients(100);

-- Stored Procedure to Generate Appointments
DELIMITER $$

CREATE PROCEDURE GenerateAppointments(IN num_appointments INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE patient_id INT;
    DECLARE doctor_id INT;
    DECLARE appointment_date DATETIME;
    WHILE i <= num_appointments DO
        SET patient_id = FLOOR(1 + (RAND() * 100));
        SET doctor_id = FLOOR(1 + (RAND() * 15));
        SET appointment_date = DATE_ADD('2025-01-01 08:00:00', INTERVAL FLOOR(RAND() * 365) DAY);
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, reason)
        VALUES (
            patient_id,
            doctor_id,
            appointment_date,
            CONCAT('Routine check-up for patient ', patient_id)
        );
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- Call the procedure to generate 200 appointments
CALL GenerateAppointments(200);
