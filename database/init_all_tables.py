"""
Script to ensure all tables needed by clinic frontend exist in the active database
(both PostgreSQL and SQLite).
"""
import sys
import os
from backend.config import config
from backend import db as database

def init_tables():
    conn = database.get_connection()
    db_type = config.DB_TYPE
    print(f"Creating tables for db_type={db_type}...")

    if db_type == 'postgres':
        sql = """
        CREATE TABLE IF NOT EXISTS medical_reports (
            id SERIAL PRIMARY KEY,
            patient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            report_title VARCHAR(200) NOT NULL,
            report_category VARCHAR(50) DEFAULT 'Other',
            test_name VARCHAR(200),
            test_date DATE,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            issuing_lab_or_hospital VARCHAR(200),
            file_name VARCHAR(255) NOT NULL,
            file_storage_path VARCHAR(500) NOT NULL,
            file_size_bytes INTEGER DEFAULT 0,
            file_mime_type VARCHAR(100) DEFAULT 'application/pdf',
            processing_status VARCHAR(30) DEFAULT 'Completed',
            extracted_raw_text TEXT,
            doctor_interpretation TEXT,
            doctor_follow_up_notes TEXT
        );

        CREATE TABLE IF NOT EXISTS report_summaries (
            id SERIAL PRIMARY KEY,
            report_id INTEGER NOT NULL REFERENCES medical_reports(id) ON DELETE CASCADE,
            ai_summary_text TEXT NOT NULL,
            key_findings TEXT,
            normal_metrics TEXT,
            abnormal_metrics TEXT,
            questions_for_doctor TEXT,
            source_grounding_disclaimer VARCHAR(500) DEFAULT 'AI-generated summary based strictly on document text. Not a clinical diagnosis.',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS report_extracted_measurements (
            id SERIAL PRIMARY KEY,
            report_id INTEGER NOT NULL REFERENCES medical_reports(id) ON DELETE CASCADE,
            test_metric_name VARCHAR(100) NOT NULL,
            observed_value NUMERIC(10, 3) NOT NULL,
            unit VARCHAR(30) NOT NULL,
            reference_range_low NUMERIC(10, 3),
            reference_range_high NUMERIC(10, 3),
            status_flag VARCHAR(20) DEFAULT 'Normal',
            notes VARCHAR(255)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            patient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            doctor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            appointment_date DATE NOT NULL,
            appointment_time VARCHAR(20) NOT NULL,
            consultation_type VARCHAR(20) DEFAULT 'Online',
            status VARCHAR(20) DEFAULT 'Confirmed',
            reason_for_visit VARCHAR(500),
            doctor_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS medicine_reminders (
            id SERIAL PRIMARY KEY,
            patient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            medicine_name VARCHAR(150) NOT NULL,
            dosage VARCHAR(100) NOT NULL,
            reminder_time VARCHAR(10) NOT NULL,
            days_of_week VARCHAR(100) DEFAULT 'Daily',
            start_date DATE DEFAULT CURRENT_DATE,
            end_date DATE,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS health_timeline_events (
            id SERIAL PRIMARY KEY,
            patient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            event_type VARCHAR(50) NOT NULL,
            event_title VARCHAR(200) NOT NULL,
            event_date DATE NOT NULL,
            event_time VARCHAR(20),
            short_description VARCHAR(500),
            organization_or_doctor VARCHAR(200),
            record_reference_id INTEGER,
            status_badge VARCHAR(50) DEFAULT 'Completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS doctor_applications (
            id SERIAL PRIMARY KEY,
            doctor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            status VARCHAR(30) DEFAULT 'Pending',
            submitted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by_admin_id INTEGER REFERENCES users(id),
            review_notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS doctor_verification_reviews (
            id SERIAL PRIMARY KEY,
            application_id INTEGER NOT NULL,
            admin_user_id INTEGER NOT NULL REFERENCES users(id),
            action_taken VARCHAR(50) NOT NULL,
            reason_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pharmacy_providers (
            id SERIAL PRIMARY KEY,
            provider_name VARCHAR(100) NOT NULL UNIQUE,
            base_url VARCHAR(300) NOT NULL,
            search_url_template VARCHAR(500),
            category_tag VARCHAR(50) DEFAULT 'Pharmacy',
            is_active INTEGER DEFAULT 1,
            logo_url VARCHAR(300)
        );
        """
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        print("Postgres tables created successfully.")

    else:
        # SQLite
        sql = """
        CREATE TABLE IF NOT EXISTS medical_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            report_title TEXT NOT NULL,
            report_category TEXT DEFAULT 'Other',
            test_name TEXT,
            test_date DATE,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            issuing_lab_or_hospital TEXT,
            file_name TEXT NOT NULL,
            file_storage_path TEXT NOT NULL,
            file_size_bytes INTEGER DEFAULT 0,
            file_mime_type TEXT DEFAULT 'application/pdf',
            processing_status TEXT DEFAULT 'Completed',
            extracted_raw_text TEXT,
            doctor_interpretation TEXT,
            doctor_follow_up_notes TEXT
        );

        CREATE TABLE IF NOT EXISTS report_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL REFERENCES medical_reports(id) ON DELETE CASCADE,
            ai_summary_text TEXT NOT NULL,
            key_findings TEXT,
            normal_metrics TEXT,
            abnormal_metrics TEXT,
            questions_for_doctor TEXT,
            source_grounding_disclaimer TEXT DEFAULT 'AI-generated summary based strictly on document text. Not a clinical diagnosis.',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS report_extracted_measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            report_id INTEGER NOT NULL REFERENCES medical_reports(id) ON DELETE CASCADE,
            test_metric_name TEXT NOT NULL,
            observed_value REAL NOT NULL,
            unit TEXT NOT NULL,
            reference_range_low REAL,
            reference_range_high REAL,
            status_flag TEXT DEFAULT 'Normal',
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            doctor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            appointment_date DATE NOT NULL,
            appointment_time TEXT NOT NULL,
            consultation_type TEXT DEFAULT 'Online',
            status TEXT DEFAULT 'Confirmed',
            reason_for_visit TEXT,
            doctor_notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS medicine_reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            medicine_name TEXT NOT NULL,
            dosage TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            days_of_week TEXT DEFAULT 'Daily',
            start_date DATE DEFAULT CURRENT_DATE,
            end_date DATE,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS health_timeline_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            event_type TEXT NOT NULL,
            event_title TEXT NOT NULL,
            event_date DATE NOT NULL,
            event_time TEXT,
            short_description TEXT,
            organization_or_doctor TEXT,
            record_reference_id INTEGER,
            status_badge TEXT DEFAULT 'Completed',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS doctor_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            status TEXT DEFAULT 'Pending',
            submitted_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_by_admin_id INTEGER REFERENCES users(id),
            review_notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS doctor_verification_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_id INTEGER NOT NULL,
            admin_user_id INTEGER NOT NULL REFERENCES users(id),
            action_taken TEXT NOT NULL,
            reason_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS pharmacy_providers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider_name TEXT NOT NULL UNIQUE,
            base_url TEXT NOT NULL,
            search_url_template TEXT,
            category_tag TEXT DEFAULT 'Pharmacy',
            is_active INTEGER DEFAULT 1,
            logo_url TEXT
        );
        """
        conn.executescript(sql)
        conn.commit()
        print("SQLite tables created successfully.")

    database.close_connection(conn)

if __name__ == '__main__':
    init_tables()
