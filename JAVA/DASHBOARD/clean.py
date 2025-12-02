import pandas as pd
import numpy as np

# --- 1. Load the data ---
try:
    df = pd.read_csv('advanced_students_dataset.csv')
    print("--- Original Data Info ---")
    df.info()
except FileNotFoundError:
    print("Error: 'data.csv' not found. Please check the file path.")
    exit()

# --- 2. Handle Missing Values (NaN/None) ---
## a. Check for missing values
print("\n--- Missing Values Count Per Column ---")
print(df.isnull().sum())

## b. Strategy 1: Remove rows with ANY missing values (use cautiously)
# df_cleaned_dropped = df.dropna()

## c. Strategy 2: Fill missing values (Imputation)
# For numerical columns (e.g., 'Age', 'Salary'): fill with the mean or median
numerical_cols = df.select_dtypes(include=np.number).columns
for col in numerical_cols:
    df[col].fillna(df[col].mean(), inplace=True) 

# For categorical columns (e.g., 'Gender', 'City'): fill with the mode (most frequent) or a constant
categorical_cols = df.select_dtypes(include=['object']).columns
for col in categorical_cols:
    df[col].fillna(df[col].mode()[0], inplace=True) # Fills with the most frequent value

# --- 3. Handle Duplicates ---
## a. Check for duplicates
print(f"\nTotal duplicate rows found: {df.duplicated().sum()}")

## b. Remove duplicate rows, keeping the first occurrence
df.drop_duplicates(inplace=True)

# --- 4. Correct Data Types (If necessary) ---
# Example: Convert a column that should be numeric but is stored as object (string)
# df['Numerical_Column'] = pd.to_numeric(df['Numerical_Column'], errors='coerce') 
# 'errors="coerce"' will turn non-convertible values into NaN, which you can then fill (Step 2)

# Example: Convert a column to datetime objects
# df['Date_Column'] = pd.to_datetime(df['Date_Column'], errors='coerce')

# --- 5. Handle Inconsistent Data / Standardize Categorical Data ---
# Example: Standardizing 'Yes'/'yes'/'Y' to just 'Yes' in a 'Status' column
# df['Status'] = df['Status'].str.lower().str.replace('y', 'yes').replace({'yes': 'Yes'})

# Example: Trimming whitespace from object columns
for col in categorical_cols:
    if df[col].dtype == 'object':
        df[col] = df[col].str.strip()

# --- 6. Review and Save the Cleaned Data ---
print("\n--- Cleaned Data Info ---")
df.info()

# Display the first few rows of the cleaned data
print("\n--- First 5 Rows of Cleaned Data ---")
print(df.head())

# Save the cleaned data to a new CSV file
df.to_csv('cleaned_data.csv', index=False)
print("\nSuccessfully saved cleaned data to 'cleaned_data.csv'")