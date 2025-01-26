-- Create a new schema
CREATE DATABASE IF NOT EXISTS university;

USE university;

-- Table: departments
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: professors
CREATE TABLE IF NOT EXISTS professors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department_id INT NOT NULL,
    hire_date DATE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- Table: students
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    department_id INT NOT NULL,
    enrollment_year YEAR NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- Table: courses
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    department_id INT NOT NULL,
    credits INT NOT NULL,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

-- Table: enrollments
CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrollment_date DATE NOT NULL,
    grade CHAR(1),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
);

-- Preload departments data
INSERT INTO departments (name) VALUES
('Computer Science'),
('Mathematics'),
('Physics'),
('Biology'),
('Chemistry');

-- Preload professors data
INSERT INTO professors (name, department_id, hire_date, email) VALUES
('Dr. Alice', 1, '2010-09-01', 'alice@university.edu'),
('Dr. Bob', 2, '2012-03-15', 'bob@university.edu'),
('Dr. Charlie', 3, '2008-07-22', 'charlie@university.edu'),
('Dr. Diana', 4, '2015-05-10', 'diana@university.edu'),
('Dr. Eve', 5, '2011-01-30', 'eve@university.edu');

-- Preload students data
INSERT INTO students (name, email, department_id, enrollment_year) VALUES
('John Doe', 'john.doe@university.edu', 1, 2022),
('Jane Smith', 'jane.smith@university.edu', 2, 2021),
('Michael Brown', 'michael.brown@university.edu', 3, 2020),
('Emily Davis', 'emily.davis@university.edu', 4, 2019),
('Chris Wilson', 'chris.wilson@university.edu', 5, 2018),
('Sophia Johnson', 'sophia.johnson@university.edu', 1, 2023),
('Daniel Martinez', 'daniel.martinez@university.edu', 2, 2022),
('Olivia Garcia', 'olivia.garcia@university.edu', 3, 2021),
('James Hernandez', 'james.hernandez@university.edu', 4, 2020),
('Isabella Moore', 'isabella.moore@university.edu', 5, 2019);

-- Preload courses data
INSERT INTO courses (name, department_id, credits) VALUES
('Introduction to Programming', 1, 3),
('Data Structures', 1, 4),
('Linear Algebra', 2, 3),
('Calculus I', 2, 3),
('Classical Mechanics', 3, 4),
('Quantum Physics', 3, 4),
('Cell Biology', 4, 3),
('Genetics', 4, 3),
('Organic Chemistry', 5, 4),
('Inorganic Chemistry', 5, 3);

-- Preload enrollments data
INSERT INTO enrollments (student_id, course_id, enrollment_date, grade) VALUES
(1, 1, '2023-09-01', 'A'),
(1, 2, '2023-09-01', 'B'),
(2, 3, '2022-09-01', 'A'),
(2, 4, '2022-09-01', 'B'),
(3, 5, '2021-09-01', 'C'),
(3, 6, '2021-09-01', 'A'),
(4, 7, '2020-09-01', 'B'),
(4, 8, '2020-09-01', 'A'),
(5, 9, '2019-09-01', 'C'),
(5, 10, '2019-09-01', 'B'),
(6, 1, '2024-01-15', 'A'),
(6, 2, '2024-01-15', 'B'),
(7, 3, '2023-10-01', 'A'),
(7, 4, '2023-10-01', 'B'),
(8, 5, '2023-08-15', 'C'),
(8, 6, '2023-08-15', 'B'),
(9, 7, '2023-06-01', 'A'),
(9, 8, '2023-06-01', 'B'),
(10, 9, '2023-05-01', 'A'),
(10, 10, '2023-05-01', 'B'),
(1, 3, '2023-09-15', 'A'),
(1, 4, '2023-09-15', 'B'),
(2, 5, '2022-10-10', 'B'),
(2, 6, '2022-10-10', 'A'),
(3, 7, '2021-11-11', 'C'),
(3, 8, '2021-11-11', 'A'),
(4, 9, '2020-12-12', 'B'),
(4, 10, '2020-12-12', 'C'),
(5, 1, '2019-01-13', 'A'),
(5, 2, '2019-01-13', 'B');
