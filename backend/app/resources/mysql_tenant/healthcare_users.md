1. Admin User

{
    "context_user_identifier_value" : "admin1@hospital.com"
}

{
    "user_id": "admin1@hospital.com",
    "custom_fields": {
        "user_id": 1,
        "email": "admin1@hospital.com",
        "role": "admin",
        "contact_number": "999-777-7823-83",
        "is_active": "TRUE",
        "is_admin": "TRUE"
    },
}

Valid Inputs: "Can you get count the users with nurse role that are on a Department named Neurology alias the result as total_count"
Output: 
{
    "total_count": 30
}

Valid Inputs: "Can you count the number of appointments present"
{
    "appointment_count": 500
}


Valid Inputs:  "Can you get me the user with role nurse with the highest count of patient_assignments"
Output:
{
    "user_id": 17,
    "name": "Nurse User 3",
    "patient_assignment_count": 9
}

Synonyms: patient_assignments became nurse_patient



Invalid Ambigous Input: "Can you get me the all details of a User with role of nurse who has the highest count of patient_assignments and the Department is from Cardiology"
Output:
{
    "user_query_scope": {
            "intent": "fetch_data",
            "entities": {
                "tables": [
                    "users",
                    "nurse_patient",
                    "departments"
                ],
                "columns": [
                    "users.user_id",
                    "users.name",
                    "users.email",
                    "users.contact_number",
                    "users.role",
                    "users.is_active",
                    "users.is_admin",
                    "users.created_at",
                    "nurse_patient.nurse_patient_id",
                    "nurse_patient.patient_id",
                    "nurse_patient.assigned_date",
                    "departments.department_id",
                    "departments.department_name",
                    "departments.created_at"
                ],
                "sensitive_columns": []
            }
    },
    "error_message": "(pymysql.err.OperationalError) (1054, \"Unknown column 'p.department_id' in 'on clause'\")"
}

Input: "Retrieve the top user with role nurse who has the highest number of assigned nurse_patient and its assigned department is on Cardiology"
Output: 
{
    "user_id": 17,
    "name": "Nurse User 3",
    "department_name": "Cardiology"
}

Enabled INCLUDE_QUERY_SCOPE_ON_SQL_GENERATION Setting on SQL_GENERATION, if disabled will throw an error.


Input:   "Can you get me the total count of nurses and doctors thar are working on Neurology Department?"
Output:
{
    "total_nurses": 8,
    "total_doctors": 3
}

