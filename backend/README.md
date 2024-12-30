docker-compose up -d
docker-compose down --volumes --rmi all --remove-orphans

Supported Settings
```json
{
    "settings":{
        "BASE_MODEL_LLM_URL":{
            "setting_basic_name": "Base Model LLM URL",
            "setting_value": "{BASE_URL_FOR_LLM_API_URL}",
            "setting_category": "LLM_GENERATION",
            "is_custom_setting": false
        },
        "MODEL_INTENT_ENDPOINT":{
            "setting_basic_name": "Base Model Intent Endpoint",        
            "setting_value": "/intent-generation",
            "setting_category": "LLM_GENERATION",
            "is_custom_setting": false
        },
        "MODEL_GENERATION_ENDPOINT":{
            "setting_basic_name": "Base Model LLM SQL-Generation Endpoint",        
            "setting_value": "/sql-generation",
            "setting_category": "LLM_GENERATION",
            "is_custom_setting": false
        },
        "USE_DEFAULT_MODEL":{
            "setting_basic_name": "Default Toggle to use SQL-Executor's LLM Model",        
            "setting_value": "true",
            "setting_category": "LLM_GENERATION",
            "is_custom_setting": false
        }
    }
}
```

Post PoC Tasks

1. Add ITs to api/routers
2. Enforce Uniqueness of Tenant IDs and Tenant Names in tenant document collection
3. Revisit usage of root_validators
    - If single field validation use @root_validators
    - If multi field/Model scope use @validatior
4. Explore Decoupling Tables to have their own MongoDB document this is to avoid a foreseeble future where max size of 16MB will be met. 
    - Alternative Approach is to use MongoDB BSON-encoded data or use GridFS
5. Restructurize API URL
6. Revisit UT coverage for service codes
7. Under Query Scope and SQL Generation, add confidence level:
    - A threshold can be set where it will retry the output if confidence level is low
    - This can be enabled on Tenant Settings
    - Add two new boolean settings (QUERY_SCOPE_CONFIDENCE_LEVEL_THRESHOLD, SQL_GENERATION_CONFIDENCE_LEVEL_THRESHOLD)
8. Change Settings Document Schema to allow grouping of settings_category by dict-key. 
9. Create UNIFIED root level logging for Backend
10. Lessen Python model files by combining small child objects to their object parent file. 