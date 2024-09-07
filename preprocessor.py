import pandas as pd


def preprocess_and_engineer_features(data: pd.DataFrame):
    """
        Preprocess and engineer features for delivery feature.

        This function performs the following operations on the input data:
        1. Converts datetime and time columns to pandas datetime formats.
        2. Calculates the total number of service days per CMZ Code.
        3. Creates binary-encoded columns for each day of the week based on the 'Service Days' column.
        4. Calculates the total delivery period in days.

        Parameters:
                data (DataFrame): Input DataFrame containing delivery information.

        Returns:
                DataFrame: Processed DataFrame with additional engineered features.
    """
    # convert datetime and time to pandas formats
    data["Delivery End Date"] = pd.to_datetime(data["Delivery End Date"])
    data["Delivery Start Time"] = pd.to_datetime(data["Delivery Start Time"], format="%H:%M:%S").dt.time
    data["Delivery End Time"] = pd.to_datetime(data["Delivery End Time"], format="%H:%M:%S").dt.time
    data["Delivery Start Date"] = pd.to_datetime(data["Delivery Start Date"])

    # Feature Engineering
    #  get the total number of service days per CMZ Code
    data["Service Days Count"] = data["Service Days"].str.split(",").apply(len).astype(int)
    # get convert the service days to columns as binary-encoded days
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in days_of_week:
        data[day] = data["Service Days"].apply(lambda x: 1 if day in x.split(",") else 0)

    # Total delivery period
    data["Delivery Period"] = (data["Delivery End Date"] - data["Delivery Start Date"]).dt.days

    return data
