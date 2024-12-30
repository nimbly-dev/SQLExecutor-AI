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


---
New One:


SessionData:

{
    "custom_fields": {
        "role": "customer",
        "is_admin": false,
        "is_active": true,
        "sub": "customer_user_4",
        "user_id": 4
    }
}

Login:
{   
    "auth_tenant_id": "TENANT_TST2",
    "auth_field" : "customer_user_4",
    "auth_passkey_field" : "customer_user_4123"
}

Input:
{
    "input": "Show me the details of customer_info"
}

Output:
{
    "query_scope": {
        "intent": "fetch_data",
        "entities": {
            "tables": [
                "customer_info"
            ],
            "columns": [
                "customer_info.customer_id",
                "customer_info.customer_name",
                "customer_info.user_id",
                "customer_info.customer_email",
                "customer_info.phone_number",
                "customer_info.address"
            ]
        }
    },
    "user_input": "Show me the details of customer_info",
    "sql_query": "SELECT customer_id, customer_name, user_id, customer_email, phone_number, address FROM customer_info WHERE user_id = '4';",
    "sql_response": [
        {
            "customer_id": 12,
            "customer_name": "Customer 12",
            "user_id": 4,
            "customer_email": "customer12@example.com",
            "phone_number": "123-456-7812",
            "address": "12 Demo Street, Demo City, DC 10012"
        }
    ],
    "injected_str": "user_id = '4'"
}