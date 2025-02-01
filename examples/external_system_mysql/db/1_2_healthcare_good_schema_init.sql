-- --------------------------------------------------
-- 1. Drop and re-create the database to ensure a fully clean slate
-- --------------------------------------------------
DROP DATABASE IF EXISTS healthcare_good_schema;
CREATE DATABASE healthcare_good_schema;
USE healthcare_good_schema;

-- --------------------------------------------------
-- 2. Create tables
-- --------------------------------------------------

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    contact_number VARCHAR(20) UNIQUE,
    role ENUM('admin', 'doctor', 'patient', 'nurse') NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: departments
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: doctors
CREATE TABLE IF NOT EXISTS doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
);

-- Table: nurses
CREATE TABLE IF NOT EXISTS nurses (
    nurse_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(department_id) ON DELETE CASCADE
);

-- Table: patients
CREATE TABLE IF NOT EXISTS patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Table: appointments
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    nurse_id INT DEFAULT NULL,
    appointment_date TIMESTAMP NOT NULL,
    reason TEXT NOT NULL,
    UNIQUE KEY (patient_id, doctor_id, appointment_date),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE,
    FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id) ON DELETE SET NULL
);

-- Table: nurse_patient
CREATE TABLE IF NOT EXISTS nurse_patient (
    nurse_patient_id INT AUTO_INCREMENT PRIMARY KEY,
    nurse_id INT NOT NULL,
    patient_id INT NOT NULL,
    assigned_date DATE NOT NULL,
    FOREIGN KEY (nurse_id) REFERENCES nurses(nurse_id) ON DELETE CASCADE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
    UNIQUE KEY (nurse_id, patient_id)
);

-- --------------------------------------------------
-- 3. Preload department data
-- --------------------------------------------------
INSERT INTO departments (department_name) VALUES
('Cardiology'),
('Neurology'),
('Orthopedics'),
('Pediatrics'),
('General Medicine')
ON DUPLICATE KEY UPDATE department_name = VALUES(department_name);

-- --------------------------------------------------
-- 4. Stored Procedures
-- --------------------------------------------------
DELIMITER $$

-- (A) GenerateAdmins
DROP PROCEDURE IF EXISTS GenerateAdmins$$
CREATE PROCEDURE GenerateAdmins(IN num_admins INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE random_contact VARCHAR(20);

    WHILE i <= num_admins DO
        SET random_contact = CONCAT(
            '999-777-',
            LPAD(FLOOR(1000 + RAND()*8999), 4, '0'),
            '-',
            LPAD(FLOOR(RAND()*99), 2, '0')
        );

        INSERT INTO users (name, email, contact_number, role, is_active, is_admin)
        VALUES (
            CONCAT('Admin User ', i),
            CONCAT('admin', i, '@hospital.com'),
            random_contact,
            'admin',
            TRUE,
            TRUE
        );

        SET i = i + 1;
    END WHILE;
END$$

-- (B) GenerateUsers (any role)
DROP PROCEDURE IF EXISTS GenerateUsers$$
CREATE PROCEDURE GenerateUsers(IN num_users INT, IN user_role VARCHAR(20))
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE random_contact VARCHAR(20);
    DECLARE local_is_admin BOOLEAN;

    WHILE i <= num_users DO
        SET local_is_admin = IF(user_role = 'admin', TRUE, FALSE);
        SET random_contact = CONCAT(
            '999-888-',
            LPAD(FLOOR(1000 + RAND()*8999), 4, '0'),
            '-',
            LPAD(FLOOR(RAND()*99), 2, '0')
        );

        INSERT INTO users (name, email, contact_number, role, is_active, is_admin)
        VALUES (
            CONCAT(UPPER(LEFT(user_role,1)), SUBSTRING(user_role,2), ' User ', i),
            CONCAT(user_role, i, '@hospital.com'),
            random_contact,
            user_role,
            TRUE,
            local_is_admin
        );
        SET i = i + 1;
    END WHILE;
END$$

-- (C) GenerateDoctors
DROP PROCEDURE IF EXISTS GenerateDoctors$$
CREATE PROCEDURE GenerateDoctors(IN num_doctors INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE dpt_id INT;
    DECLARE doc_user_id INT;

    WHILE i <= num_doctors DO
        SET dpt_id = (
            SELECT department_id
            FROM departments
            ORDER BY RAND() LIMIT 1
        );

        SET doc_user_id = (
            SELECT user_id
            FROM users
            WHERE role = 'doctor'
              AND user_id NOT IN (SELECT user_id FROM doctors)
            ORDER BY RAND()
            LIMIT 1
        );

        IF doc_user_id IS NOT NULL THEN
            INSERT INTO doctors (user_id, department_id, hire_date)
            VALUES (
                doc_user_id,
                dpt_id,
                DATE_ADD('2010-01-01', INTERVAL FLOOR(RAND() * 5000) DAY)
            );
        END IF;

        SET i = i + 1;
    END WHILE;
END$$

-- (D) GenerateNurses
DROP PROCEDURE IF EXISTS GenerateNurses$$
CREATE PROCEDURE GenerateNurses(IN num_nurses INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE dpt_id INT;
    DECLARE nur_user_id INT;

    WHILE i <= num_nurses DO
        SET dpt_id = (
            SELECT department_id
            FROM departments
            ORDER BY RAND() LIMIT 1
        );

        SET nur_user_id = (
            SELECT user_id
            FROM users
            WHERE role = 'nurse'
              AND user_id NOT IN (SELECT user_id FROM nurses)
            ORDER BY RAND()
            LIMIT 1
        );

        IF nur_user_id IS NOT NULL THEN
            INSERT INTO nurses (user_id, department_id, hire_date)
            VALUES (
                nur_user_id,
                dpt_id,
                DATE_ADD('2015-01-01', INTERVAL FLOOR(RAND() * 2000) DAY)
            );
        END IF;

        SET i = i + 1;
    END WHILE;
END$$

-- (E) GeneratePatients
DROP PROCEDURE IF EXISTS GeneratePatients$$
CREATE PROCEDURE GeneratePatients(IN num_patients INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE pat_user_id INT;
    DECLARE g ENUM('Male','Female','Other');

    WHILE i <= num_patients DO
        SET g = IF(MOD(i, 3) = 0, 'Other',
                   IF(MOD(i, 2) = 0, 'Female', 'Male'));

        SET pat_user_id = (
            SELECT user_id
            FROM users
            WHERE role = 'patient'
              AND user_id NOT IN (SELECT user_id FROM patients)
            ORDER BY RAND()
            LIMIT 1
        );

        IF pat_user_id IS NOT NULL THEN
            INSERT INTO patients (user_id, dob, gender)
            VALUES (
                pat_user_id,
                DATE_ADD('1970-01-01', INTERVAL FLOOR(RAND() * 20000) DAY),
                g
            );
        END IF;

        SET i = i + 1;
    END WHILE;
END$$

-- (F) GenerateAppointments
DROP PROCEDURE IF EXISTS GenerateAppointments$$
CREATE PROCEDURE GenerateAppointments(IN num_appointments INT)
BEGIN
    DECLARE i INT DEFAULT 1;
    DECLARE pid INT;
    DECLARE did INT;
    DECLARE nid INT;
    DECLARE app_date DATETIME;

    WHILE i <= num_appointments DO
        SET pid = (SELECT patient_id FROM patients ORDER BY RAND() LIMIT 1);
        SET did = (SELECT doctor_id FROM doctors ORDER BY RAND() LIMIT 1);
        SET nid = (SELECT nurse_id FROM nurses ORDER BY RAND() LIMIT 1);

        IF pid IS NOT NULL AND did IS NOT NULL THEN
            SET app_date = DATE_ADD('2025-01-01 08:00:00', INTERVAL FLOOR(RAND() * 365) DAY);
            INSERT INTO appointments (patient_id, doctor_id, nurse_id, appointment_date, reason)
            VALUES (
                pid,
                did,
                nid,
                app_date,
                CONCAT('Routine check-up for patient ', pid)
            );
        END IF;

        SET i = i + 1;
    END WHILE;
END$$

-- (G) GenerateNursePatientAssignments
DROP PROCEDURE IF EXISTS GenerateNursePatientAssignments$$
CREATE PROCEDURE GenerateNursePatientAssignments(IN num_assignments INT)
BEGIN
    DECLARE total_possible INT;

    /*
      Label the inner code block so that we can LEAVE properly
      in case total_possible = 0.
    */
    main_block: BEGIN
        SET total_possible = (
            SELECT COUNT(*) FROM nurses
        ) * (
            SELECT COUNT(*) FROM patients
        );

        IF total_possible = 0 THEN
            -- If there's no nurses or no patients, do nothing and exit block
            LEAVE main_block;
        END IF;

        IF num_assignments > total_possible THEN
            -- Instead of throwing an error, we cap the number
            SET num_assignments = total_possible;
        END IF;

        INSERT INTO nurse_patient (nurse_id, patient_id, assigned_date)
        SELECT n.nurse_id,
               p.patient_id,
               DATE_ADD('2020-01-01', INTERVAL FLOOR(RAND() * 2000) DAY)
        FROM nurses n
        CROSS JOIN patients p
        ORDER BY RAND()
        LIMIT num_assignments;
    END main_block;

END$$

DELIMITER ;

-- --------------------------------------------------
-- 5. Execute the stored procedures in the correct order
-- --------------------------------------------------

CALL GenerateAdmins(4);
CALL GenerateUsers(10, 'doctor');
CALL GenerateUsers(30, 'nurse');
CALL GenerateUsers(100, 'patient');

CALL GenerateDoctors(10);
CALL GenerateNurses(30);
CALL GeneratePatients(100);

CALL GenerateAppointments(500);
CALL GenerateNursePatientAssignments(150);

-- --------------------------------------------------
-- 6. (Optional) Verify data after insertion
-- --------------------------------------------------
-- SELECT COUNT(*) AS total_doctors FROM doctors;
-- SELECT COUNT(*) AS total_nurses FROM nurses;
-- SELECT COUNT(*) AS total_patients FROM patients;
-- SELECT COUNT(*) AS total_appointments FROM appointments;
-- SELECT COUNT(*) AS total_nurse_patients FROM nurse_patient;
