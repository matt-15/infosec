import schedule
import scipy
from scipy import stats
import statistics as st
from datetime import datetime

#row = [1,2]
#time_ = ['2021-01-15T11:55:06+0800', '2021-01-15T11:55:07+0800']
#action = ['SELECT','SELECT']
#time_delta = [0,30]
buffer = [0]


def threat_calculation():
    no_lines = 0

    log_root = open("log/IDSin.txt", 'r')
    output_log = open("log/IDSout.txt", 'a')
    internal_log = open("log/IDSinternal.txt", 'r')
    log_read_counter = log_root.read()
    log_read_by_line = log_read_counter.split("\n")
    log_root.flush()
    internal_log.flush()
    i_log_read_counter = internal_log.read()  # internal log is empty for some reason
    i_log_read_by_line = i_log_read_counter.split("\n")
    log_read_by_line.pop()
    log_read = log_read_by_line[-1]
    splitted_list = log_read.split(',')
    line_id = splitted_list[1]  #latest ID, most recent log
    line_id = int(line_id)
    try:
        line_counter = str(eval(i_log_read_by_line[4]))
    except:
        line_counter = 0
    line_val = line_counter
    print(line_val, line_id)
    for i in log_read_by_line:
        if i:
            no_lines += 1
    if no_lines < 0: #change this value back to 10 later
        print("Insufficient data points provided, threat calculation will be skipped")
    else:
        internal_log.close()
        while int(line_val) < no_lines:
            try:
                internal_log = open("log/IDSinternal.txt", 'r')
            except:
                print("Exception occurred when reading")
                print(internal_log)
            i_log_read_counter = internal_log.read()
            i_log_read_by_line = i_log_read_counter.split("\n")
            print(i_log_read_by_line[0])
            line_val = int(line_val)
            splitted_list3 = log_read_by_line[line_val].split(',')
            try:
                row = eval(i_log_read_by_line[0])
                time_ = i_log_read_by_line[1]
                action = eval(i_log_read_by_line[2])
                time_delta = eval(i_log_read_by_line[3])
                line_val = int(eval(i_log_read_by_line[4]))
            except:
                row = []
                time_ = 0
                action = []
                time_delta = []
                line_val = 0
            if line_val >= line_id:  #If previous ID = latest ID
                print("Waiting for log update...")
                break

            else:  #elif line_val + 1 >= line_id:
                print("Transaction being parsed: ", log_read_by_line[line_val].split(','))
                if len(row) < 2 or len(action) < 2:
                    print('row empty')
                else:
                    time_delta[0] = 0.0
                    row_deviation = st.stdev(row)
                    row_mean = st.mean(row)
                    time_delta_deviation = st.stdev(time_delta)
                    time_delta_mean = st.mean(time_delta)


                    row_multi = 1  # Multipliers to be implemented with ML down the road
                    time_delta_multi = 1
                    action_multi = 1

                    if row_deviation == 0:
                        row_deviation = 0.00001
                    if time_delta_deviation == 0:
                        time_delta_deviation = 0.00001

                    z_row = (int(splitted_list3[3]) - row_mean) / row_deviation  # log_read means that it is current iteration not latest, - sum of the mean of the row list
                    p_row = abs(50 - (scipy.stats.norm.sf(abs(z_row)) * 100))
                    z_time_delta = (int(splitted_list3[1]) - time_delta_mean) / time_delta_deviation
                    p_time_delta = abs(50 - (scipy.stats.norm.sf(abs(z_time_delta)) * 100))
                    p_action = len(action) / action.count(splitted_list3[2])

                    threat_score = ((p_row * row_multi) + (p_time_delta * time_delta_multi) + (p_action * action_multi))
                    print(p_row * row_multi)
                    print(threat_score)
                    if threat_score > 100:
                        threat_level = 4
                    elif threat_score >= 50:
                        threat_level = 3
                    elif threat_score >= 30:
                        threat_level = 2
                    elif threat_score <30 :
                        threat_level = 1

                    if threat_level == 1:
                        print("Threat level 1 detected, ignoring...")
                    elif threat_level == 2:
                        print("Threat level 2 detected, ignoring...")
                    elif threat_level == 3:
                        log = 'it xavier'
                        print("Threat level 3 detected, logging...")
                        output_log.flush()
                        output_log.write('%s %s %s\n' %('Transaction',splitted_list3,'is a high level threat (3)'))
                        output_log.flush()
                    elif threat_level == 4:
                        print("Threat level 4 detected, logging...")
                        output_log.flush()
                        output_log.write('%s %s %s\n' % ('Transaction', splitted_list3, 'is a very high level threat (4)'))
                        output_log.flush()
                line_counter = int(line_counter)
                line_counter += 1
                line_counter = str(line_counter)
                row.append(int(splitted_list3[3]))
                action.append(splitted_list3[2])
                time_ = []
                time_.append(splitted_list3[0])
                splitted_list2 = log_read_by_line[line_val - 1].split(',')
                prev_time = splitted_list2[0]  # Replace the numeral with wherever the row position is in the log
                line_val += 1
                time_ = datetime.strptime(time_[0], '%Y-%m-%dT%H:%M:%S%z')
                prev_time = datetime.strptime(prev_time, '%Y-%m-%dT%H:%M:%S%z')
                last_read_id = line_val
                try:
                    delta = time_ - prev_time
                    delta = delta.total_seconds()
                    time_delta.append(delta)

                except:
                    exit()

                internal_log = open("log/IDSinternal.txt", 'w')
                internal_log.write('%s\n%s\n%s\n%s\n%s\n' % (row, time_, action, time_delta, last_read_id))
                internal_log.close()

schedule.every(1).seconds.do(threat_calculation)
while True:
    schedule.run_pending()
