

**Test Query 1: Multi-Table Query with Specific Columns**
Input:
> "Show me the customer name, the product categories they purchased, and the total amount they spent from the customers and orders tables."

Expected Output:
```json
{
    "intent": "fetch_data",
    "entities": {
        "tables": ["customers", "orders"],
        "columns": [
            "customers.customer_name",
            "orders.*"
        ]
    }
}
```

#### Explanation:
- The model identifies two tables: `customers` and `orders`.
- `customers.customer_name` is an explicit column.
- "total amount they spent" is ambiguous (possibly an aggregation). The fallback column scope for `orders` is `"orders.*"`.

---

**Test Query 2: Ambiguous Query with Aggregation**
 Input:
> "Retrieve the details of all transactions completed in the last 7 days, including the total amount for each customer."

Expected Output:
```json
{
    "intent": "fetch_data",
    "entities": {
        "tables": ["transactions", "customers"],
        "columns": [
            "transactions.*",
            "customers.*"
        ]
    }
}
```

Explanation:
- The model identifies the `transactions` and `customers` tables from "all transactions" and "each customer."
- Since specific columns are not explicitly mentioned, the model uses `"transactions.*"` and `"customers.*"` as broad scopes.

---

**Test Query 3: Complex Join Query**
Input:
> "Get the order IDs, customer names, and product categories for all orders where the total order value exceeded $500."

Expected Output:
```json
{
    "intent": "fetch_data",
    "entities": {
        "tables": ["orders", "customers", "products"],
        "columns": [
            "orders.order_id",
            "customers.customer_name",
            "products.product_category"
        ]
    }
}
```

Explanation:
- The model identifies the `orders`, `customers`, and `products` tables based on the query's context.
- The columns are explicit: `orders.order_id`, `customers.customer_name`, and `products.product_category`.
- "total order value" is ignored as an aggregation and does not appear as a column.
