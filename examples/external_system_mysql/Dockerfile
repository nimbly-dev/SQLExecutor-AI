# Start from the official MySQL image
FROM mysql:8.0

# Copy all SQL files into the initialization directory
COPY ./db /docker-entrypoint-initdb.d/

# Set permissions for the SQL files
RUN chmod -R 644 /docker-entrypoint-initdb.d

# Expose the MySQL port
EXPOSE 3306
