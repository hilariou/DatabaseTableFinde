import random
from faker import Faker
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Boolean, DATETIME, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import func 

# Default Database Configuration
DEFAULT_USERNAME = 'root'       # Default MySQL username
DEFAULT_PASSWORD = ''            # Default empty password; modify if needed
DEFAULT_SERVER_IP = '127.0.0.1'  # Default local server IP; modify if needed
DEFAULT_DATABASE_NAME = 'cent_bank_db'  # Default database name

# Construct the database URI
DATABASE_URI = f'mysql+pymysql://{DEFAULT_USERNAME}:{DEFAULT_PASSWORD}@{DEFAULT_SERVER_IP}/{DEFAULT_DATABASE_NAME}'

# Create a base class for your models
Base = declarative_base()
faker = Faker()

# Define the bank_products model
class BankProduct(Base):
    __tablename__ = 'bank_products'
    
    product_id = Column(Integer, primary_key=True, autoincrement=True)
    product_name = Column(String(100), nullable=False)
    product_type = Column(String(50), nullable=False)
    interest_rate = Column(Numeric(5, 2), nullable=True)
    min_balance = Column(Numeric(10, 2), nullable=True)
    max_loan_amount = Column(Numeric(15, 2), nullable=True)
    tenure_months = Column(Integer, nullable=True)
    is_available = Column(Boolean, default=True)
    risk_assessment_score = Column(Numeric(5, 2), nullable=True)
    eligibility_criteria = Column(Text, nullable=True)
    confidential_terms = Column(Text, nullable=True)
    created_at = Column(DATETIME, server_default=func.now())  # Use func.now() for server default
    updated_at = Column(DATETIME, server_default=func.now(), onupdate=func.now())  # Update on changes
# Generate random bank product data
def generate_random_product():
    product_names = ["Home Loan", "Personal Loan", "Student Loan", "Auto Loan", "Small Business Loan", "Mortgage", "Savings Account", "Fixed Deposit", "Current Account"]
    product_types = ["Loan", "Savings", "Deposit", "Investment"]

    return BankProduct(
        product_name=random.choice(product_names),
        product_type=random.choice(product_types),
        interest_rate=round(random.uniform(3.0, 15.0), 2),  # Interest rate between 3% and 15%
        min_balance=round(random.uniform(0.0, 10000.0), 2) if random.choice([True, False]) else None,  # Random min balance or None
        max_loan_amount=round(random.uniform(1000.0, 1000000.0), 2),  # Max loan amount between 1,000 and 1,000,000
        tenure_months=random.randint(12, 360),  # Tenure between 1 year and 30 years
        is_available=random.choice([True, False]),
        risk_assessment_score=round(random.uniform(1.0, 5.0), 2),  # Risk score between 1 and 5
        eligibility_criteria=faker.sentence(),  # Random requirements using Faker
        confidential_terms=faker.sentence()  # Random terms using Faker
    )

# Create the table
def create_tables(engine):
    Base.metadata.create_all(engine)

# Populate the bank_products table with random data
def populate_data(session, num_records):
    products = [generate_random_product() for _ in range(num_records)]
    session.add_all(products)  # Add multiple products to the session
    session.commit()  # Commit the transaction
    print(f"Successfully inserted {num_records} records into the bank_products table.")  # Success message

def main():
    # Create the database engine
    engine = create_engine(DATABASE_URI)

    # Create all tables
    create_tables(engine)

    # Create a new session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Define the number of records to generate
    num_records = 100  # Change this number to generate more or fewer records
    populate_data(session, num_records)

    # Close the session
    session.close()

if __name__ == '__main__':
    main()