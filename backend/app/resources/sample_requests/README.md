### 1.  Input: 
**"Show me the customer name, the product categories they purchased, and the total amount they spent from the customers and orders tables."**


| **User**           | **Password**           | **`customers` Access** | **`orders` Access** | **Accessible Columns (`customers`)**       | **Accessible Columns (`orders`)**                  |
|--------------------|-------------------------|-------------------------|----------------------|---------------------------------------------|----------------------------------------------------|
| **test_user**      | `test_password`        | ✅                     | ✅                   | `customer_name`, `password`                | `total_amount` (**no `product_categories`)**       |
| **admin**          | `admin_password`       | ✅                     | ✅                   | `customer_name`, `password`                | `total_amount`, `product_categories`, `password`  |
| **limited_user**   | `limited_password`     | ❌                     | ✅                   | N/A                                         | `total_amount`, `product_categories`, `password`  |
| **specific_user@example.com**  | `specific_password`    | ✅                     | ✅                   | `customer_name` (**no `password`)          | `order_date`, `order_id` (**no `total_amount`)**   |
| **inactive_user**  | `inactive_password`    | ❌                     | ❌                   | N/A                                         | N/A                                                |
| **sales_rep_user** | `sales_rep_password`   | Conditional (VIP)      | ✅                   | Conditional (`password` if VIP)            | `total_amount`, `product_categories`, `password`  |
| **payment_processor** | `payment_password` | ❌                     | ✅                   | N/A                                         | `payment_id`, `payment_date`, `amount_paid`       |

