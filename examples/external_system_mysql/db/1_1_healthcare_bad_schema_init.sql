-- Create a new schema
CREATE DATABASE IF NOT EXISTS healthcare_bad_schema;

USE healthcare_bad_schema;

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    contact_number VARCHAR(15) UNIQUE,
    role ENUM('admin', 'doctor', 'patient', 'nurse') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: departments
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: doctors
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- Table: nurses
CREATE TABLE IF NOT EXISTS nurses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- Table: patients
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Table: appointments
CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    nurse_id INT DEFAULT NULL,
    appointment_date TIMESTAMP NOT NULL,
    reason TEXT NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (nurse_id) REFERENCES nurses(id) ON DELETE SET NULL
);

-- Mapping table for nurse-patient relationships
CREATE TABLE nurse_patient (
    nurse_id INT NOT NULL,
    patient_id INT NOT NULL,
    assigned_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (nurse_id, patient_id),
    FOREIGN KEY (nurse_id) REFERENCES nurses(id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

-- Preload departments data
INSERT INTO departments (name) VALUES
('Cardiology'),
('Neurology'),
('Orthopedics'),
('Pediatrics'),
('General Medicine');

-- Stored Procedure to Generate Users
DELIMITER $$

CREATE PROCEDURE GenerateUsers(IN num_users INT, IN role ENUM('admin', 'doctor', 'patient', 'nurse'))
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE is_admin BOOLEAN;
    DECLARE random_contact_number VARCHAR(15);
    WHILE i <= num_users DO
        SET is_admin = IF(role = 'admin', TRUE, FALSE);
        SET random_contact_number = CONCAT('999-888-', LPAD(FLOOR(1 + (RAND() * 9999)), 4, '0')); -- Random 4-digit number
        INSERT INTO users (name, email, contact_number, role, is_active, is_admin)
        VALUES (
            CONCAT(UPPER(LEFT(role, 1)), LOWER(SUBSTRING(role, 2)), ' User ', i),
            CONCAT(role, i, '@hospital.com'),
            random_contact_number,
            role,
            TRUE,
            is_admin
        )
        ON DUPLICATE KEY UPDATE contact_number = CONCAT('999-888-', LPAD(FLOOR(10000 + (RAND() * 90000)), 5, '0')); -- Ensure unique fallback
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;


-- Generate users
CALL GenerateUsers(5, 'admin');
CALL GenerateUsers(20, 'doctor');
CALL GenerateUsers(10, 'nurse');
CALL GenerateUsers(50, 'patient');

-- Stored Procedure to Generate Doctors
DELIMITER $$

CREATE PROCEDURE GenerateDoctors(IN num_doctors INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE department_id INT;
    DECLARE user_id INT;
    WHILE i <= num_doctors DO
        SET department_id = FLOOR(1 + (RAND() * 5)); -- Random department between 1 and 5
        SET user_id = (SELECT id FROM users WHERE role = 'doctor' AND id NOT IN (SELECT user_id FROM doctors) ORDER BY RAND() LIMIT 1);
        INSERT INTO doctors (user_id, department_id, hire_date)
        VALUES (user_id, department_id, DATE_ADD('2010-01-01', INTERVAL FLOOR(RAND() * 5000) DAY));
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- Generate doctors
CALL GenerateDoctors(20);

-- Stored Procedure to Generate Nurses
DELIMITER $$

CREATE PROCEDURE GenerateNurses(IN num_nurses INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE department_id INT;
    DECLARE user_id INT;
    WHILE i <= num_nurses DO
        SET department_id = FLOOR(1 + (RAND() * 5)); -- Random department between 1 and 5
        SET user_id = (SELECT id FROM users WHERE role = 'nurse' AND id NOT IN (SELECT user_id FROM nurses) ORDER BY RAND() LIMIT 1);
        INSERT INTO nurses (user_id, department_id, hire_date)
        VALUES (user_id, department_id, DATE_ADD('2015-01-01', INTERVAL FLOOR(RAND() * 2000) DAY));
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- Generate nurses
CALL GenerateNurses(10);

-- Stored Procedure to Generate Patients
DELIMITER $$

CREATE PROCEDURE GeneratePatients(IN num_patients INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE user_id INT;
    DECLARE gender ENUM('Male', 'Female', 'Other');
    WHILE i <= num_patients DO
        SET gender = IF(MOD(i, 3) = 0, 'Other', IF(MOD(i, 2) = 0, 'Female', 'Male'));
        SET user_id = (SELECT id FROM users WHERE role = 'patient' AND id NOT IN (SELECT user_id FROM patients) ORDER BY RAND() LIMIT 1);
        INSERT INTO patients (user_id, dob, gender)
        VALUES (
            user_id,
            DATE_ADD('1970-01-01', INTERVAL FLOOR(RAND() * 20000) DAY),
            gender
        );
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- Generate patients
CALL GeneratePatients(50);

-- Stored Procedure to Generate Appointments
DELIMITER $$

CREATE PROCEDURE GenerateAppointments(IN num_appointments INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE patient_id INT;
    DECLARE doctor_id INT;
    DECLARE nurse_id INT;
    DECLARE appointment_date DATETIME;
    WHILE i <= num_appointments DO
        SET patient_id = (SELECT id FROM patients ORDER BY RAND() LIMIT 1);
        SET doctor_id = (SELECT id FROM doctors ORDER BY RAND() LIMIT 1);
        SET nurse_id = (SELECT id FROM nurses ORDER BY RAND() LIMIT 1);
        SET appointment_date = DATE_ADD('2025-01-01 08:00:00', INTERVAL FLOOR(RAND() * 365) DAY);
        INSERT INTO appointments (patient_id, doctor_id, nurse_id, appointment_date, reason)
        VALUES (
            patient_id,
            doctor_id,
            nurse_id,
            appointment_date,
            CONCAT('Routine check-up for patient ', patient_id)
        );
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- Generate appointments
CALL GenerateAppointments(100);

-- Stored Procedure to Assign Nurses to Patients
DELIMITER $$

CREATE PROCEDURE AssignNursesToPatients(IN num_assignments INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE nurse_id INT;
    DECLARE patient_id INT;
    WHILE i <= num_assignments DO
        SET nurse_id = (SELECT id FROM nurses ORDER BY RAND() LIMIT 1);
        SET patient_id = (SELECT id FROM patients ORDER BY RAND() LIMIT 1);
        INSERT INTO nurse_patient (nurse_id, patient_id, assigned_date)
        VALUES (nurse_id, patient_id, CURRENT_TIMESTAMP)
        ON DUPLICATE KEY UPDATE assigned_date = CURRENT_TIMESTAMP;
        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;

-- Assign nurses to patients
CALL AssignNursesToPatients(50);
