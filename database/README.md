# Database Documentation — AI Health Clinic

## Purpose
This directory contains the production-grade Oracle Database SQL DDL/DML scripts and entity-relationship models for **AI Health Clinic**.

## Files
1. `sql/01_create_tables.sql`: Generates all 25 core tables with identity columns, check constraints, default timestamps, and foreign key relationships.
2. `sql/02_constraints_and_indexes.sql`: Builds B-tree indexes for high-frequency queries on patient records, timeline sorting, appointment schedules, and doctor status filters.
3. `sql/03_seed_test_data.sql`: Populates the database with realistic synthetic data matching the user interface, including:
   - Patient: Rohan Sharma (`patient@clinic.com`)
   - Doctors: Dr. Amit Verma, Dr. Priya Mehta, Dr. Rahul Singh, Dr. Neha Kapoor
   - Pending doctor applicants for verification queue
   - Medical reports (CBC, Chest X-Ray, Brain MRI, Prescription, Urine Routine)
   - Unified Health Timeline events
   - Drug reference catalogue & 7 official Indian pharmacy destinations
4. `sql/04_sample_queries.sql`: Demonstrates production queries for timeline assembly, lab value comparisons, doctor queues, and security audit logs.
5. `sql/05_cleanup_test_data.sql`: Drops all tables cleanly with `CASCADE CONSTRAINTS`.
6. `diagrams/er_diagram.md`: Full Mermaid ER diagram of data relationships.

## How to Connect to Oracle Database
1. Run SQL scripts in your Oracle instance (e.g., Oracle XE, Cloud Autonomous Database, or Oracle Live SQL):
   ```sql
   @sql/01_create_tables.sql
   @sql/02_constraints_and_indexes.sql
   @sql/03_seed_test_data.sql
   ```
2. Configure credentials in `.env`:
   ```env
   DB_ENGINE=oracle
   ORACLE_USER=admin
   ORACLE_PASSWORD=YourPassword
   ORACLE_DSN=localhost:1521/XEPDB1
   ```
3. When running in a lightweight development environment without a live Oracle server, set `DB_ENGINE=sqlite` to automatically create and seed the identical schema in SQLite (`ai_health_clinic.db`) with zero manual setup.
