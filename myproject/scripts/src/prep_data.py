import pandas as pd


# Data Cleaning and Data Processing
def process_data(
        result_path: str,
        exclude_username: str,
        old_username: str,
        new_username: str,
        start_year: str,
        finish_year: str,):

    df = pd.read_csv(result_path)

    # Transform data to datetime format
    df["date"] = pd.to_datetime(df["date"], utc=True)

    # Creation new attributes in df
    df["year"] = df["date"].dt.year
    df["year"] = df["year"].astype(int)

    df["utc_hour"] = df["date"].dt.hour

    df["month_year"] = df["date"].dt.strftime('%Y-%m')
    df['month_year'] = pd.to_datetime(df['month_year'], format='%Y-%m')

    # Extract the part before '@' to create new column 'Username'
    df['username'] = df['email'].str.split('@').str[0]

    # Extract repo name
    df['repo'] = df['repo'].str.split('/').str[-1]

    # Filtering data
    # Exclude the username
    df = df[~df['username'].isin(exclude_username)]

    # Replace all occurrences of old username with new username
    df['username'] = df['username'].replace(old_username, new_username)

    # Transfer username to lower case
    df['username'] = df['username'].str.lower()

    # Filter years
    df = df[(df['date'].dt.year >= start_year) & (df['date'].dt.year <= finish_year)]

    # Filter last year and creation filtered df with data for the last year graphs
    last_year = pd.Timestamp.today().year - 1
    last_year_df = df[df['month_year'].dt.year == last_year]

    return df, last_year_df


def explore_data(df: pd.DataFrame):
    # Show all columns and set display width for better readability
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    # Display the first few rows of the dataframe
    print("Data preview:")
    print(df.head())

    # Display column names
    print("\nColumn names:")
    print(df.columns)

    # Check data types and number of rows
    print("\nData types and info:")
    print(df.info())

    # Check missing values in each column
    print("\nMissing values per column:")
    print(df.isnull().sum())

    # Check for duplicated rows
    print("\nDuplicated rows:")
    print(df.duplicated().sum())

    # Statistical summary for numerical columns
    print("\nStatistical summary:")
    print(df.describe())
