# Access Control Test Scenarios

This document outlines updated test scenarios for validating access control across various user roles.

| **User Type**       | **Username**                   | **Password**       | **Accessible Tables**                                                                                     |
|----------------------|--------------------------------|--------------------|----------------------------------------------------------------------------------------------------------|
| **Normal User**      | `test_user`                   | `test_password`   | **Orders**: `order_id`, `customer_id`, `order_date`<br>**Customers**: `customer_id`, `name`, `email`     |
| **Specific User**    | `specific_user@example.com`   | `specific_password`| **Orders**: `order_id`, `order_date`, `total_amount`<br>**Customers**: `customer_id`, `name`, `email` |
| **Elevated User**    | `elevated_user`               | `elevated_password`| **Orders**: `order_id`, `customer_id`, `order_date`, `total_amount`<br>**Customers**: All columns |
| **Inactive User**    | `inactive_user`               | `inactive_password`| **None** (User is inactive)                                                                             |
| **Admin User**       | `admin`                       | `admin_password`   | **Orders**: All columns (excluding globally denied `password`)<br>**Customers**: All columns (excluding globally denied `password` and `credit_card_number`)<br>**Payments**: All columns (excluding globally denied `credit_card_number` and `password`) |

---

### Sample Inputs per User Type

#### Normal User:
```json
{
    "input": "Show me the order_id, customer_id, and order_date for orders"
}
```

#### Specific User:
```json
{
    "input": "Show me the order_id, order_date, and total_amount for orders, and for customers, show me customer_id, name, and email"
}
```

#### Elevated User:
```json
{
    "input": "Show me the order_id, customer_id, order_date, and total_amount for orders, and for customers, show me all available columns"
}
```

#### Inactive User:
```json
{
    "input": "Show me the order_id, and customer_id for orders"
}
```

#### Admin User:
```json
{
    "input": "Show me all columns for orders, customers, and payments excluding globally restricted ones"
}
```

---

### Notes
1. Wildcard (`*`) is resolved to all columns dynamically based on the schema, excluding globally denied columns.
2. **Inactive User** has no access as the `active` field in the session data is `false`.
3. Inputs are specified with explicit column references for better debugging and validation.
4. Elevated and Admin users have access to all columns in tables they are allowed, respecting global restrictions.
