# Database Setup Guide

This guide explains how to create and configure the PostgreSQL database for SpendSmart.

## Prerequisites

- PostgreSQL installed on your system
- PostgreSQL server running

### Check if PostgreSQL is installed:
```bash
psql --version
```

### Check if PostgreSQL is running:
```bash
# On macOS
brew services list | grep postgresql

# On Linux
sudo systemctl status postgresql

# Or try connecting
psql -U postgres
```

## Method 1: Using Command Line (Recommended)

### Step 1: Connect to PostgreSQL
```bash
# Default connection (uses your system user)
psql postgres

# Or with specific user
psql -U postgres

# Or with host and port
psql -h localhost -U postgres -d postgres
```

### Step 2: Create the Database
Once connected to PostgreSQL, run:
```sql
CREATE DATABASE spendsmart;
```

### Step 3: Create a User (Optional but Recommended)
```sql
-- Create a new user
CREATE USER spendsmart_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE spendsmart TO spendsmart_user;
```

### Step 4: Exit PostgreSQL
```sql
\q
```

### Step 5: Update Your .env File
Update your `DATABASE_URL` in `.env`:

**If using default user:**
```
DATABASE_URL=postgresql://your_username@localhost:5432/spendsmart
```

**If using created user:**
```
DATABASE_URL=postgresql://spendsmart_user:your_secure_password@localhost:5432/spendsmart
```

**Format breakdown:**
```
postgresql://[username]:[password]@[host]:[port]/[database_name]
```

## Method 2: Using createdb Command (Quick Method)

If you have PostgreSQL command-line tools installed:

```bash
# Create database with default settings
createdb spendsmart

# Or with specific user
createdb -U postgres spendsmart
```

Then update your `.env` file with the appropriate `DATABASE_URL`.

## Method 3: Using pgAdmin (GUI Method)

1. Open pgAdmin (PostgreSQL administration tool)
2. Connect to your PostgreSQL server
3. Right-click on "Databases" → "Create" → "Database"
4. Enter database name: `spendsmart`
5. Click "Save"

## Method 4: Using Docker (If you prefer containerized setup)

```bash
# Run PostgreSQL in Docker
docker run --name spendsmart-db \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=spendsmart \
  -p 5432:5432 \
  -d postgres:15

# Your DATABASE_URL would be:
# DATABASE_URL=postgresql://postgres:your_password@localhost:5432/spendsmart
```

## Verify Database Creation

After creating the database, verify it exists:

```bash
# List all databases
psql -l

# Or connect directly to the database
psql -d spendsmart
```

## Initialize Database Tables

Once your database is created and `DATABASE_URL` is configured in `.env`, the application will automatically create the required tables when you first run it:

```bash
python main.py <plaid_access_token>
```

Or you can manually initialize:

```python
from database import init_db
init_db()
```

## Common Issues

### Issue: "database does not exist"
**Solution:** Make sure you've created the database and the name in `DATABASE_URL` matches exactly.

### Issue: "password authentication failed"
**Solution:** 
- Check your password in `DATABASE_URL`
- Verify PostgreSQL user exists and has correct password
- Check `pg_hba.conf` for authentication settings

### Issue: "connection refused"
**Solution:**
- Make sure PostgreSQL server is running
- Check if PostgreSQL is listening on the correct port (default: 5432)
- Verify firewall settings

### Issue: "permission denied"
**Solution:**
- Grant necessary privileges to your database user
- Make sure the user has CREATE privileges on the database

## Database Connection String Examples

**Local development (default user, no password):**
```
DATABASE_URL=postgresql://localhost:5432/spendsmart
```

**Local with user and password:**
```
DATABASE_URL=postgresql://username:password@localhost:5432/spendsmart
```

**Remote database:**
```
DATABASE_URL=postgresql://username:password@host.example.com:5432/spendsmart
```

**With SSL (for production):**
```
DATABASE_URL=postgresql://username:password@host:5432/spendsmart?sslmode=require
```

## Next Steps

After creating the database:

1. ✅ Database created
2. ✅ Update `.env` file with correct `DATABASE_URL`
3. ✅ Run the application - tables will be created automatically
4. ✅ Start tracking your expenses!

