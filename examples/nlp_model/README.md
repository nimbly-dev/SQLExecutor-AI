We will use OpenAI's gpt-4o-mini model to generate our SQL queries. For testing here are some sample queries


1. Fetch Single Column

```json
{
    "schema": "{\"filter_rules\":{\"allowed_columns\":[\"email\"],\"denied_columns\":[],\"condition\":\"users.user_id = 123\"},\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"}}}}}",
    "prompt": "Get my email address."
}
```

OUTPUT:

```json
{
    "schema": "{\"filter_rules\":{\"allowed_columns\":[\"email\"],\"denied_columns\":[],\"condition\":\"users.user_id = 123\"},\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"}}}}}",
    "prompt": "Get my email address.",
    "output": "SELECT email FROM users WHERE user_id = 123;"
}
```

2. Join Tables

```json
{
    "schema": "{\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"}}},\"orders\":{\"description\":\"Stores order information\",\"columns\":{\"order_id\":{\"type\":\"INTEGER\"},\"user_id\":{\"type\":\"INTEGER\"},\"amount\":{\"type\":\"DECIMAL\"},\"order_date\":{\"type\":\"DATE\"}}}}}",
    "prompt": "Show all orders along with user names."
}
```

OUTPUT:

```json
{
    "schema": "{\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"}}},\"orders\":{\"description\":\"Stores order information\",\"columns\":{\"order_id\":{\"type\":\"INTEGER\"},\"user_id\":{\"type\":\"INTEGER\"},\"amount\":{\"type\":\"DECIMAL\"},\"order_date\":{\"type\":\"DATE\"}}}}}",
    "prompt": "Show all orders along with user names.",
    "output": "SELECT orders.order_id, users.name, orders.amount, orders.order_date\nFROM orders\nJOIN users ON orders.user_id = users.user_id;"
}
```

3. Aggregation

```json
{
    "schema": "{\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"}}},\"orders\":{\"description\":\"Stores order information\",\"columns\":{\"order_id\":{\"type\":\"INTEGER\"},\"user_id\":{\"type\":\"INTEGER\"},\"amount\":{\"type\":\"DECIMAL\"},\"order_date\":{\"type\":\"DATE\"}}}}}",
    "prompt": "Get the total amount spent by each user."
}
```

OUTPUT:
```json
{
    "schema": "{\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"}}},\"orders\":{\"description\":\"Stores order information\",\"columns\":{\"order_id\":{\"type\":\"INTEGER\"},\"user_id\":{\"type\":\"INTEGER\"},\"amount\":{\"type\":\"DECIMAL\"},\"order_date\":{\"type\":\"DATE\"}}}}}",
    "prompt": "Get the total amount spent by each user.",
    "output": "SELECT user_id, SUM(amount) AS total_spent\nFROM orders\nGROUP BY user_id;"
}
```

4. Advanced Joins
```json
{
    "schema": "{\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"}}},\"orders\":{\"description\":\"Stores order information\",\"columns\":{\"order_id\":{\"type\":\"INTEGER\"},\"user_id\":{\"type\":\"INTEGER\"},\"amount\":{\"type\":\"DECIMAL\"},\"order_date\":{\"type\":\"DATE\"}}},\"products\":{\"description\":\"Stores product details\",\"columns\":{\"product_id\":{\"type\":\"INTEGER\"},\"product_name\":{\"type\":\"TEXT\"},\"price\":{\"type\":\"DECIMAL\"}}}}}",
    "prompt": "Find the names of users who purchased 'Laptop' products along with the total amount they spent."
}
```

OUTPUT:
```json
{
    "schema": "{\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"}}},\"orders\":{\"description\":\"Stores order information\",\"columns\":{\"order_id\":{\"type\":\"INTEGER\"},\"user_id\":{\"type\":\"INTEGER\"},\"amount\":{\"type\":\"DECIMAL\"},\"order_date\":{\"type\":\"DATE\"}}},\"products\":{\"description\":\"Stores product details\",\"columns\":{\"product_id\":{\"type\":\"INTEGER\"},\"product_name\":{\"type\":\"TEXT\"},\"price\":{\"type\":\"DECIMAL\"}}}}}",
    "prompt": "Find the names of users who purchased 'Laptop' products along with the total amount they spent.",
    "output": "SELECT u.name, SUM(o.amount) AS total_spent\nFROM users u\nJOIN orders o ON u.user_id = o.user_id\nJOIN products p ON o.product_id = p.product_id\nWHERE p.product_name = 'Laptop'\nGROUP BY u.name;"
}
```

5. Multi-Condition Queries

```json
{
    "schema": "{\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"},\"company\":{\"type\":\"TEXT\"}}},\"orders\":{\"description\":\"Stores order information\",\"columns\":{\"order_id\":{\"type\":\"INTEGER\"},\"user_id\":{\"type\":\"INTEGER\"},\"amount\":{\"type\":\"DECIMAL\"},\"order_date\":{\"type\":\"DATE\"}}}}}",
    "prompt": "Retrieve the names of users who work at 'TechCorp' and have placed orders after January 1, 2022, spending more than $100."
}
```

Output:
```json
{
    "schema": "{\"tables\":{\"users\":{\"description\":\"Stores user account information\",\"columns\":{\"user_id\":{\"type\":\"INTEGER\"},\"name\":{\"type\":\"TEXT\"},\"email\":{\"type\":\"TEXT\"},\"company\":{\"type\":\"TEXT\"}}},\"orders\":{\"description\":\"Stores order information\",\"columns\":{\"order_id\":{\"type\":\"INTEGER\"},\"user_id\":{\"type\":\"INTEGER\"},\"amount\":{\"type\":\"DECIMAL\"},\"order_date\":{\"type\":\"DATE\"}}}}}",
    "prompt": "Retrieve the names of users who work at 'TechCorp' and have placed orders after January 1, 2022, spending more than $100.",
    "output": "SELECT DISTINCT users.name \nFROM users \nJOIN orders ON users.user_id = orders.user_id \nWHERE users.company = 'TechCorp' \nAND orders.order_date > '2022-01-01' \nAND orders.amount > 100;"
}
```