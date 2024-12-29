This is a sample external system project that can be used to dev test locally the SQLExecutor Project. 
When setting up a Test Tenant, take note of the API key, tables, and how-to-authenticate in this Application
Here are the tables and its access control:

Access Control:

1. Customer User: Has access to customer_info, user
2. Customer Representative: Has access to customer_info, payments, orders
   - Accountant: Has access to Payments amounts related but not Orders
   - Customer Support: Hass acces to Orders related but not Payments
3. Admin Has access to all table

roles=['admin','customer','customer_support','accountant']

--- 

1. **users**:  
   - `user_id` 
   - `username`: `str`  
   - `password`: `str`  
   - `email`: `str` 
   - `created_at`: `timestamp` 

2. **roles_list**:  
   - `role`: `str`  
   - `user_id` 

3. **customer_info**:  
   - `customer_id` 
   - `customer_name`: `str`  
   - `user_id` 
   - `customer_email`: `str`  
   - `phone_number`: `str` 
   - `address`: `str` 

4. **payments**:  
   - `payment_id` 
   - `user_id` 
   - `amount`: `decimal` 
   - `payment_date`: `timestamp`
   - `status`: `str` 

5. **orders**:  
   - `order_id` 
   - `user_id`
   - `order_date`: `timestamp` 
   - `total_amount`: `decimal`
   - `status`: `str` 

6. **admin**:  
   - `admin_id` 
   - `username`: `str`  
   - `password`: `str`  
   - `email`: `str` 
