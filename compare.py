import pandas as pd
import os
import json
import sys

# get the current working directory
cwd = os.getcwd()

# get the input JSON file.
input_JSON = os.path.join(cwd, "data", "input.json")
# load the JSON file into a variable
input_data = json.load(open(input_JSON))
# get the data object from input_data variable
# if we need we can also ensure the node is available
data = input_data["info"]

for info in data:
    print("Summary: " + info["description"])
    # get the expected JSON file
    expected = os.path.join(cwd, "inputs" ,"expected" ,info["expected"])
    # get the actual JSON file
    actual = os.path.join(cwd, "inputs", "actual" ,info["actual"])
    # diff path
    diff = os.path.join(cwd, "inputs", "diff" ,info["diff"])
    # summary path
    summary = os.path.join(cwd, "inputs", "diff", info["summary"])
    # common identity column with unique value between two CSV files to compare
    identity = info["identity"]
    # check the actual and expected CSV files are present
    # if not present intimate not present and stop execution
    if(not os.path.exists(expected) and not os.path.exists(actual)):
        # we can modify the custom message as needed
        print("## file in expected or actual path not present")
        sys.exit(0)
    else:
        # read the expected, actual CSV file
        expected_CSV = pd.read_csv(expected, encoding="utf-8")
        actual_CSV = pd.read_csv(actual, encoding="utf-8")
        # sort the expected file and actual file with same axis
        expected_CSV = expected_CSV.sort_index(axis=1)
        actual_CSV = actual_CSV.sort_index(axis=1)
        # get all the expected column names as list
        expected_CSV_col = list(expected_CSV)
        # add suffix _expected for all expected column names
        expected_CSV_sfx = expected_CSV.add_suffix("_expected")
        # add suffix _actual for all actual column names
        actual_CSV_sfx = actual_CSV.add_suffix("_actual")
        # Outer Join expected and actual csv with identity
        comparision = pd.merge(expected_CSV_sfx, actual_CSV_sfx, how="outer", left_on=identity + "_expected", right_on=identity + "_actual")
        # create new column for every expected column with suffix '_compare'
        # compare each column and update the value comparision to '_compare' column
        for col in expected_CSV_col:
            comparision[(col + "_#compare")] = comparision[(col + "_actual")].fillna("-") == comparision[(col + "_expected")].fillna("-")
        # reorder the columns
        comparision = comparision.reindex(sorted(comparision.columns), axis=1)
        # write as CSV into diff folder
        comparision.to_csv(diff)
        
        # Create summary for display
        
        # create new data frame with columns True and False
        logdf = pd.DataFrame(index=[True, False])
        # collect the expected column names with suffix '_#compare'
        check_column = [x + "_#compare" for x in expected_CSV_col]
        # app
        for col in check_column:
            # show True value count and False value total count for each col
            col_info = comparision[col].value_counts()
            # create new data frame with each col
            col_df = pd.DataFrame(col_info)
            # add informations one by one
            logdf = logdf.join(col_df, how="outer")
        # transpose the the logdf
        logdf = logdf.transpose()
        # fill the NaN with 0
        logdf = logdf.fillna(0)
        # format the float values as number
        pd.options.display.float_format = "{:,.0f}".format
        # create new column 'Total' and add True and False count values
        logdf["Total"] = logdf.apply(lambda x: x[True] + x[False], axis=1)
        # rename the 'True' column as 'Match' and 'False' column as 'Difference'
        logdf = logdf.rename(columns={True: 'Match', False : 'Difference'})
        logdf.to_csv(summary)
        print(logdf)