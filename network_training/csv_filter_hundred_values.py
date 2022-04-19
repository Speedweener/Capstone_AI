import pandas as pd
from collections import Counter
import csv



def filter_hundred(filename):
    old_filename = filename + '.csv'
    new_filename = filename + '_NEW.csv'
    # df = pd.read_csv(old_filename)
    # func_holder = df['batch'].tolist()
    # count_dict = Counter(func_holder)
    # print(count_dict)
    #
    # bad_rows = []
    #
    # for i in count_dict:
    #     if count_dict[i] != 100:
    #         bad_rows.append(str(i))
    counter = 1
    key_file = open("key_value", 'r+')
    data = int(key_file.read())
    num_rows = 0

    with open(old_filename) as count_file:
        for rows in count_file:
            num_rows += 1
    print(num_rows)
    with open(old_filename) as csv_file:
        with open(new_filename, mode='w', newline='') as output_file:
            employee_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[1] == 'q0_wrist':
                    continue
                row[0] = data
                employee_writer.writerow(row)
                if counter == 100:
                    data += 1
                    counter = 0
                    if num_rows - int(csv_reader.line_num) < 100:
                        key_file.seek(0)
                        key_file.write(str(data))
                        key_file.truncate()
                        key_file.close()
                        break

                counter += 1

if __name__ == "__main__":
    # 0 idle, 1 Grenade   2 Shield    3 Reload     4 Logout
    import os

    # assign directory
    directory = 'group_data'

    # iterate over files in
    # that directory
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            filter_hundred(f[0:-4])



