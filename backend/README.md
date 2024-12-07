docker-compose up -d
docker-compose down --volumes --rmi all --remove-orphans

Post PoC Tasks

1. Add ITs to api/routers
2. Enforce Uniqueness of Tenant IDs and Tenant Names in tenant collection
3. Revisit usage of root_validators
    - If single field validation use @root_validators
    - If multi field/Model scope use @validatior