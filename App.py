
#Importing libraries
import pandas as pd 
import streamlit as st 

#Application configuration
st.title("Temple University AI reiemburstment assisant")
st.header("Faculty and Staff Reimbursment ")
st.divider()
uploaded_file = st.file_uploader("Upload Expense Report | File type: CSV, PDF", type=None,max_upload_size=1024)


#Data analysis (columns)
def analyze_columns(df):
    identify_data_types(df)
    for index, column in enumerate(df.columns):
        st.write(
            f"Column {index}: {column}"
        )

        st.write(
            f"Data type: {df[column].dtype}"
        )

        st.write(
            "Sample values:",
            df[column].dropna().head(3).tolist()
        )

        st.divider()

def identify_data_types(df):
    for column in df.columns:
        values = df[column].dropna()

        if values.empty:
            data_type = "Empty"

        elif is_date_column(values):
            data_type = "Date"

        elif pd.api.types.is_numeric_dtype(values):
            data_type = "Numeric"

        else:
            data_type = "Text"

        st.write(f"{column}: {data_type}")
# def identify_data_types(df):
#     for column in df.columns:
#         values = df[column].dropna()

#         if values.empty:
#             data_type = "Empty"

#         elif pd.api.types.is_numeric_dtype(values):
#             data_type = "Numeric"

#         else:
#             data_type = "Text or Date"
def is_date_column(values):
    values = values.dropna()

    if values.empty:
        return False

    if pd.api.types.is_numeric_dtype(values):
        return False

    sample = values.head(10)

    converted = pd.to_datetime(sample, errors="coerce")

    return converted.notna().mean() >= 0.8   

def identify_expense_date(df):
    for column in df.columns:

        # Check whether the column contains dates
        if is_date_column(df[column]):

            # Look for words associated with expense dates
            if "expense" in column or "purchase" in column or "transaction" in column:
                return column

    return None   

def normalize_expenses(df):
    standardized_df = pd.DataFrame(index=df.index)

    expense_date_column = identify_expense_date(df)

    if expense_date_column is not None:
        standardized_df["expense_date"] = pd.to_datetime(
            df[expense_date_column],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")
    else:
        standardized_df["expense_date"] = pd.NA

    return standardized_df


# Find a column using possible names
def find_column(df, possible_names):
    for name in possible_names:
        if name in df.columns:
            return name

    return None


# Identify the expense date
def identify_expense_date(df):
    column = find_column(df, [
        "expense_date",
        "transaction_date",
        "purchase_date",
        "date",
        "purchase_day"
    ])

    if column is not None and is_date_column(df[column]):
        return column

    return None


# Identify the vendor
def identify_vendor(df):
    return find_column(df, [
        "vendor",
        "merchant",
        "merchant_name",
        "seller",
        "paid_to",
        "payment_recipient"
    ])


# Identify the expense amount
def identify_amount(df):
    return find_column(df, [
        "original_amount",
        "total_paid",
        "transaction_amount",
        "expense_amount",
        "amount",
        "total"
    ])


# Identify the currency
def identify_currency(df):
    return find_column(df, [
        "currency",
        "original_currency",
        "transaction_currency",
        "currency_code"
    ])


# Identify the expense category
def identify_expense_type(df):
    return find_column(df, [
        "concur_expense_type",
        "expense_type",
        "expense_category",
        "category",
        "transaction_type"
    ])


# Identify the description
def identify_description(df):
    return find_column(df, [
        "description",
        "expense_description",
        "transaction_description",
        "details",
        "notes"
    ])


# Identify the receipt reference
def identify_receipt(df):
    return find_column(df, [
        "receipt_filename",
        "receipt",
        "receipt_file",
        "receipt_reference",
        "attachment"
    ])


# Standardize reimbursement information
def normalize_expenses(df):

    standardized_df = pd.DataFrame(index=df.index)

    column_mapping = {
        "vendor": identify_vendor(df),
        "original_amount": identify_amount(df),
        "currency": identify_currency(df),
        "expense_type": identify_expense_type(df),
        "description": identify_description(df),
        "receipt_filename": identify_receipt(df)
    }

    # Standardize expense dates
    date_column = identify_expense_date(df)

    if date_column is not None:
        standardized_df["expense_date"] = pd.to_datetime(
            df[date_column],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")
    else:
        standardized_df["expense_date"] = pd.NA

    # Standardize other reimbursement fields
    for standard_name, original_column in column_mapping.items():

        if original_column is not None:
            standardized_df[standard_name] = df[original_column]
        else:
            standardized_df[standard_name] = pd.NA

    return standardized_df

def validate_expenses(df):

    required_fields = [
        "expense_date",
        "vendor",
        "original_amount",
        "currency",
        "expense_type",
        "description",
        "receipt_filename"
    ]

    missing_values = df[required_fields].isna()

    return missing_values

def validate_amounts(df):

    amounts = pd.to_numeric(
        df["original_amount"],
        errors="coerce"
    )

    invalid_amounts = amounts.notna() & (amounts <= 0)

    return invalid_amounts

def generate_validation_messages(missing_values, invalid_amounts):

    messages = []

    for index, row in missing_values.iterrows():

        missing_fields = []

        for column in missing_values.columns:
            if row[column]:
                missing_fields.append(f"Missing {column}")

        # Check for invalid expense amounts
        if invalid_amounts.loc[index]:
            missing_fields.append("Invalid expense amount")

        if missing_fields:
            messages.append(", ".join(missing_fields))
        else:
            messages.append("Complete")

    return messages
# def analyze_columns(df):
#     for index, column in enumerate(df.columns):
#         st.write(
#         f"Index: {index}, "
#         f"Column: {column}, "
#         f"Data type: {df[column].dtype}"
#         )
#Data extraction
if st.button("Extract"):
    if uploaded_file is not None:

        if uploaded_file.name.lower().endswith(".csv"):
            #st.success("Data Extracted!")
            df = pd.read_csv(uploaded_file)

            #Standardize columns 
            df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
            )

            # #Normalize reimbursment information
            # standardized_df = normalize_expenses(df)

            # #Display only standardized information
            # st.dataframe(standardized_df)

            # Normalize reimbursement information
            standardized_df = normalize_expenses(df)

            missing_values = validate_expenses(standardized_df)

            invalid_amounts = validate_amounts(standardized_df)

            standardized_df["validation_status"] = generate_validation_messages(
             missing_values,
            invalid_amounts
)

            # Display standardized results
            st.dataframe(standardized_df)

            st.success("Data analyzed successfully!")
            #st.write("Detected Columns:", df.columns.tolist())
        #st.dataframe(df)
            #Analyze each column
            #analyze_columns(df)

            #st.write("Identified expense date column:", expense_date_column)
            #st.dataframe(df)
            #st.success("Data Extracted!")

        else:
            st.warning ("File type not supported!")
    else:
        st.warning("Please upload a file!")

# def analyze_columns(df):
#     for index, column in enumerate(df.columns):
#         st.write(
#             f"Index: {index}, "
#             f"Column: {column}, "
#             f"Data type: {df[column].dtype}"
#         )
#         analyze_columns(df)
    