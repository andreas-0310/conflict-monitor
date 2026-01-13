import csv
import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, init_db
from app.models import ConflictData


def load_csv_to_db(csv_file_path: str):
    """Load data from CSV file into the database"""
    db: Session = SessionLocal()
    
    try:
        # Initialize database
        init_db()
        
        existing_count = db.query(ConflictData).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} records.")
            response = input("Do you want to clear existing data and reload? (yes/no): ")
            if response.lower() == "yes":
                db.query(ConflictData).delete()
                db.commit()
                print("Existing data cleared.")
            else:
                print("Aborting. Data not loaded.")
                return
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            records = []
            
            for row in reader:
                population = None
                if row.get('population') and row['population'].strip():
                    try:
                        population = float(row['population'])
                    except ValueError:
                        population = None
                
                events = int(row.get('events', 0) or 0)        
                score = float(row.get('score', 0) or 0)
                conflict_data = ConflictData(
                    country=row['country'].strip(),
                    admin1=row['admin1'].strip(),
                    population=population,
                    events=events,
                    score=score
                )
                records.append(conflict_data)
                
                if len(records) >= 100:
                    db.bulk_save_objects(records)
                    db.commit()
                    records = []
            
            if records:
                db.bulk_save_objects(records)
                db.commit()
        
        count = db.query(ConflictData).count()
        print(f"Successfully loaded {count} records from {csv_file_path}")
        
    except FileNotFoundError:
        print(f"Error: File {csv_file_path} not found.")
        sys.exit(1)
    except Exception as e:
        db.rollback()
        print(f"Error loading data: {str(e)}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    csv_file = sys.argv[1] if len(sys.argv) > 1 else "sample_data.csv"
    load_csv_to_db(csv_file)
