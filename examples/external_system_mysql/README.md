Connect to DB: mysql -u root -proot

Check Access to service account: 
SELECT * 
FROM information_schema.SCHEMA_PRIVILEGES 
WHERE GRANTEE = CONCAT("'my_user'", "@'%'");
