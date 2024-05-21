import re


def generate_insert_query(input_string):
    # Regular expression to extract table name and column-value pairs
    insert_regex = r"INSERT INTO `(.+)`\s+SET\s+((?:@\d+='[^']+'\s*)+)"

    # Extract table name and column-value pairs from the input string
    match = re.search(insert_regex, input_string)
    if match:
        table_name = match.group(1)
        column_value_pairs = dict(re.findall(r"@(\d+)='([^']+)'", match.group(2)))
    else:
        return None

    # Construct the INSERT INTO query
    insert_query = f"INSERT INTO `{table_name}` ("
    insert_query += ", ".join([f"`column_{index}`" for index in range(1, len(column_value_pairs) + 1)])
    insert_query += ") VALUES ("
    insert_query += ", ".join([f"'{value}'" for value in column_value_pairs.values()])
    insert_query += ");"

    return insert_query


def generate_update_query(input_string):
    # Regular expressions to extract table name, conditions, and set values
    table_regex = r"UPDATE `(.+)`\s+WHERE"
    conditions_regex = r"WHERE\s+((?:@\d+='[^']+'\s*)+)"
    set_values_regex = r"SET\s+((?:@\d+='[^']+'\s*)+)"

    # Extract table name, conditions, and set values from the input string
    table_name_match = re.search(table_regex, input_string)
    table_name = table_name_match.group(1) if table_name_match else None

    conditions_match = re.search(conditions_regex, input_string)
    set_values_match = re.search(set_values_regex, input_string)

    conditions = dict(re.findall(r"@(\d+)='([^']+)'", conditions_match.group(1)))
    set_values = dict(re.findall(r"@(\d+)='([^']+)'", set_values_match.group(1)))

    # Construct the update query
    update_query = f"UPDATE `{table_name}` SET "
    set_clause = ", ".join([f"`{column}`='{value}'" for column, value in set_values.items()])
    where_clause = " AND ".join([f"`{column}`='{value}'" for column, value in conditions.items()])
    update_query += set_clause + " WHERE " + where_clause

    return update_query

def filter_log_for_table(log_file, table_name):
    with open(log_file, 'r') as file:
        in_section = False
        section_data = []

        for line in file:
            # Check for INSERT, UPDATE, and DELETE statements related to the specified table
            if line.startswith(f'### INSERT INTO `{table_name}`') or \
                    line.startswith(f'### UPDATE `{table_name}`') or \
                    line.startswith(f'### DELETE FROM `{table_name}`'):
                in_section = True
                section_data = [line.strip()]
                continue

            # Collect data within the section
            if in_section:
                if line.startswith('### WHERE') or line.startswith('### SET') or \
                        line.startswith('###   @') or line.startswith('### VALUES'):
                    section_data.append(line.strip())
                else:
                    if section_data:
                        str = "".join(section_data).replace("#","")
                        #print("\n".join(section_data))
                        queryString = None
                        if "UPDATE" in str:
                            queryString  = generate_update_query(str)
                            #print(updateQuery)
                        elif "INSERT" in str:
                            queryString = generate_insert_query(str)

                        elif "DELETE" in str:
                            print(str)
                            queryString = None

                        # if queryString is not None and queryString:
                        #     print(queryString)
                        #print(str)

                        #print('-' * 80)  # Separator for readability
                    in_section = False
                    section_data = []

        # Print the last collected section if the file ends
        if section_data:
            print("\n".join(section_data))
            print('-' * 80)


# Specify the path to your full log file and the table name to filter
log_file_path = '/home/fa065079/Desktop/file' ## file path to bin log 
target_table = 'dbName`.`tableName'

filter_log_for_table(log_file_path, target_table)
