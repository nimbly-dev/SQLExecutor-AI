-- Create the Retail Management System Database
CREATE DATABASE IF NOT EXISTS retail_management;

USE retail_management;

-- Table: customers
CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: products
CREATE TABLE products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    supplier_id INT NOT NULL
);

-- Table: suppliers
CREATE TABLE suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(15) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: orders
CREATE TABLE orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Table: order_items
CREATE TABLE order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- Preload suppliers data
INSERT INTO suppliers (name, contact_email, contact_phone) VALUES
('Supplier A', 'supplierA@example.com', '111-222-3333'),
('Supplier B', 'supplierB@example.com', '222-333-4444'),
('Supplier C', 'supplierC@example.com', '333-444-5555'),
('Supplier D', 'supplierD@example.com', '444-555-6666'),
('Supplier E', 'supplierE@example.com', '555-666-7777');

-- Preload products data
INSERT INTO products (name, category, price, stock, supplier_id) VALUES
('Laptop', 'Electronics', 1200.00, 50, 1),
('Smartphone', 'Electronics', 800.00, 100, 1),
('Tablet', 'Electronics', 500.00, 80, 2),
('Headphones', 'Accessories', 150.00, 200, 3),
('Charger', 'Accessories', 25.00, 300, 3),
('Desk Chair', 'Furniture', 300.00, 20, 4),
('Office Desk', 'Furniture', 400.00, 15, 4),
('Notebook', 'Stationery', 5.00, 500, 5),
('Pen', 'Stationery', 2.00, 1000, 5),
('Printer', 'Electronics', 250.00, 30, 2);

-- Generate 1000 customers
INSERT INTO customers (name, email, phone) 
SELECT 
    CONCAT('Customer ', LPAD(i, 4, '0')), 
    CONCAT('customer', i, '@example.com'), 
    CONCAT('999-888-', LPAD(i % 10000, 4, '0'))
FROM 
    (SELECT @row := @row + 1 AS i FROM (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) t1, 
          (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) t2, 
          (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) t3, 
          (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) t4, 
          (SELECT 0 UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) t5, 
          (SELECT @row := 0) init) numbers
LIMIT 1000;


-- Generate orders and order_items data
DELIMITER $$

CREATE PROCEDURE GenerateOrders()
BEGIN
    DECLARE customer_id INT;
    DECLARE product_id INT;
    DECLARE quantity INT;
    DECLARE i INT DEFAULT 1;

    WHILE i <= 500 DO
        -- Random customer ID
        SET customer_id = FLOOR(1 + (RAND() * 1000));

        INSERT INTO orders (customer_id, total_amount) VALUES (customer_id, 0);

        SET @last_order_id = LAST_INSERT_ID();

        SET quantity = FLOOR(1 + (RAND() * 5));
        SET product_id = FLOOR(1 + (RAND() * 10));

        INSERT INTO order_items (order_id, product_id, quantity, price)
        SELECT @last_order_id, id, quantity, price * quantity 
        FROM products 
        WHERE id = product_id;


        UPDATE orders 
        SET total_amount = (SELECT SUM(price) FROM order_items WHERE order_id = @last_order_id)
        WHERE id = @last_order_id;

        SET i = i + 1;
    END WHILE;
END$$

DELIMITER ;


CALL GenerateOrders();
