Here is a regenerated set of **test scenarios** based on the provided users, roles, and ruleset. Scenarios consider both `is_active` status and role-based access policies.

---

### **Regenerated Test Scenarios**

| **User Identifier**      | **Role**               | **Is Active** | **Input Query**                                                                                       | **Expected Access**     | **Reason**                                                                                           |
|---------------------------|------------------------|---------------|-------------------------------------------------------------------------------------------------------|--------------------------|-------------------------------------------------------------------------------------------------------|
| **`customer_user_1`**     | Normal User           | `false`       | `Show me the order_id, customer_id, and order_date for orders`                                        | ❌ Denied                | `is_active == false`: no access to tables or columns.                                                |
| **`customer_user_4`**     | Normal User           | `true`        | `Show me the order_id, customer_id, and order_date for orders`                                        | ✅ Allowed               | Matches **`customer_group`** policy: customers can access these specific columns in `orders`.        |
| **`admin_user_3`**        | Admin User            | `false`       | `Show me all columns for orders and payments excluding globally restricted ones`                      | ❌ Denied                | `is_active == false`: no access to tables or columns, even as admin.                                 |
| **`admin_user_8`**        | Admin User            | `true`        | `Show me all columns for orders, customers, and payments excluding globally restricted ones`          | ✅ Allowed               | Matches **`admin_group`** policy: admins can access `*` for these tables, excluding globally denied columns. |
| **`customer_support_9`**  | Specific User         | `false`       | `Show me the order_id, order_date, and total_amount for orders`                                       | ❌ Denied                | `is_active == false`: no access to tables or columns.                                                |
| **`customer_support_20`** | Specific User         | `true`        | `Show me the order_id, customer_id, and total_amount for orders`                                      | ✅ Allowed               | Matches **`customer_support_group`** policy: customer support users can access these columns.        |
| **`accountant_user_10`**  | Elevated User         | `true`        | `Show me all columns for payments`                                                                    | ✅ Allowed               | Matches **`accountant_group`** policy: accountants have access to all columns in `payments`.         |
| **`accountant_user_14`**  | Elevated User         | `false`       | `Show me all columns for payments`                                                                    | ❌ Denied                | `is_active == false`: no access to tables or columns.                                                |
| **`inactive_user`**       | Inactive User         | `false`       | `Show me the order_id and customer_id for orders`                                                     | ❌ Denied                | `is_active == false`: no access to tables or columns.                                                |
| **`specific_user@example.com`** | Specific User   | `true`        | `Show me the customer_id, name, and email for customers, and order_id, order_date for orders`         | ✅ Allowed               | Matches **`customer_support_group`** or equivalent policies: specific columns allowed for specific users. |
| **`customer_user_7`**     | Normal User           | `false`       | `Show me all columns for customers`                                                                   | ❌ Denied                | `is_active == false`: no access to tables or columns.                                                |
| **`customer_user_18`**    | Normal User           | `true`        | `Show me the order_id, customer_id, and order_date for orders where status='shipped'`                 | ✅ Allowed               | Matches **`customer_group`** policy: customers can filter accessible columns.                        |
| **`admin_user_16`**       | Admin User            | `true`        | `Show me all columns for users and payments excluding globally restricted ones`                       | ✅ Allowed               | Matches **`admin_group`** policy: admins can access all columns except globally denied ones.         |
| **`admin_user_22`**       | Admin User            | `true`        | `Show me all columns for customers and orders excluding globally restricted ones`                     | ✅ Allowed               | Matches **`admin_group`** policy: admins can access all columns except globally denied ones.         |
| **`customer_user_13`**    | Normal User           | `false`       | `Show me the order_id and total_amount for orders`                                                    | ❌ Denied                | `is_active == false`: no access to tables or columns.                                                |
| **`customer_user_23`**    | Normal User           | `true`        | `Show me the customer_id, customer_name, and customer_email for customers`                            | ✅ Allowed               | Matches **`customer_group`** policy: customers can access these columns in `customer_info`.          |
| **`customer_user_24`**    | Normal User           | `false`       | `Show me the order_id, customer_id, and order_date for orders`                                        | ❌ Denied                | `is_active == false`: no access to tables or columns.                                                |

---

### **Notes**
1. **Active vs. Inactive Users:**
   - Inactive users (`is_active == false`) are denied all access, regardless of their role.
   - Active users are granted access according to their role's group policy.

2. **Role-Specific Policies:**
   - **Normal Users (`customer`):** Limited to specific columns in `orders` and `customer_info`.
   - **Admins:** Nearly full access to all columns, excluding globally denied ones (`password`, etc.).
   - **Customer Support:** Specific access to columns in `orders`.
   - **Accountants:** Full access to columns in `payments`.

3. **Global Restrictions:**
   - Denied columns like `password` are universally excluded across all roles.

4. **Dynamic Columns (`*`):**
   - Wildcard access (`*`) dynamically resolves to columns allowed under the group or global policies.