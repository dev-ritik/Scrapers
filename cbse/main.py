import csv
import datetime
import random
import sys
import time
from typing import Optional

import requests
from bs4 import BeautifulSoup
from orderedset import OrderedSet
from requests.adapters import HTTPAdapter
from urllib3 import Retry

session = requests.Session()

retry = Retry(connect=5, backoff_factor=0.2)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


def attempt(roll: int, dob: datetime.date) -> (int, Optional[bytes]):
    url = "https://resultsarchives.nic.in/cbseresults/cbseresults2014/class10/cbse102014_all.asp"

    payload = {'regno': roll,
               'dob': dob.strftime('%d/%m/%Y'),
               'B1': 'Submit'}

    rand = random.uniform(0, 1)
    time.sleep(2 + rand * 2.2)

    user_agents = ['Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 '
                   'Safari/537.36',
                   'Mozilla/5.0 (Windows NT 5.1; rv:9.0.1) Gecko/20100101 Firefox/9.0.1',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/60.0.3112.113 Safari/537.36']
    headers = {
        'authority': 'resultsarchives.nic.in',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'origin': 'https://resultsarchives.nic.in',
        'upgrade-insecure-requests': '1',
        'dnt': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': user_agents[int(rand * 4) % 4],
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://resultsarchives.nic.in/cbseresults/cbseresults2014/class10/cbse102014_all.htm',
        'accept-language': 'en-US,en;q=0.9'
    }

    response = session.post(url, headers=headers, data=payload, timeout=30)

    if response.status_code != 200:
        log.write("Error Status code: %d\n" % response.status_code)
        print("fatal error", file=sys.stderr)
        return -1, None
    if response.text.__contains__('Result Not Found'):
        return 0, None
    else:
        return 1, response.content


START_DOB = datetime.date(1999, 12, 31)
END_DOB = datetime.date(1996, 1, 1)
START_ROLL = <start>
END_ROLL = <end>

paths = sys.argv
if len(paths) == 2:
    start_roll = int(paths[1].strip())
else:
    print(f"Using {START_ROLL} as start roll")
    start_roll = START_ROLL

record = {}


def flatten_json(b: {}, delim: str) -> {}:
    val = {}
    for i in b.keys():
        if isinstance(b[i], dict):
            get = flatten_json(b[i], delim)
            for j in get.keys():
                val[i + delim + j] = get[j]
        elif isinstance(b[i], list):
            for k in range(len(b[i])):
                get = flatten_json(b[i][k], delim)
                for j in get.keys():
                    val[f"{i}{delim}{k}{delim}{j}"] = get[j]
        else:
            val[i] = b[i]
    return val


def get_next_roll(temp_roll: int, change: bool = True) -> int:
    if change:
        temp_roll += 1
    while temp_roll not in record:
        if temp_roll > 7128500:
            return temp_roll
        temp_roll += 1
    return temp_roll


def get_next_date(current_date: datetime.date) -> datetime.date:
    current_date -= datetime.timedelta(days=1)
    if current_date == START_DOB:
        current_date = END_DOB - datetime.timedelta(days=1)
    return current_date


def get_data_template(roll: int, name: str, mother_name: str, father_name: str, dob: datetime.date) -> {}:
    return {
        'Roll': roll,
        'Name': name,
        'Mother\'s name': mother_name,
        'Father\'s name': father_name,
        'DoB': dob,
        'CGPA': 0,
        'Academic': [],
        'Co Curricular': [],
        'Co Scholastic': [],
    }


def get_subject_template(code: int, name: str, fa: str, sa: str, total: str, gp: str) -> {}:
    return {
        'code': code,
        'name': name,
        'Formative': fa,
        'Summative': sa,
        'Total': total,
        'GP': gp,
    }


def get_misc_subject_template(code_name: str, grade: str) -> {}:
    return {
        'code - name': code_name,
        'Grade': grade,
    }


def parse_html(content: Optional[bytes]) -> {}:
    content = BeautifulSoup(content, "html.parser")
    main_table = content.find_all('table')[5].find_all('tr', recursive=False)
    details_row = main_table[3].find_all('td')
    acads_row = main_table[4]
    co_curricular_row = main_table[6]
    co_scholastic_row = main_table[7]

    profile = get_data_template(details_row[2].text, details_row[4].text, details_row[6].text, details_row[8].text,
                                details_row[10].text)

    acads = acads_row.find_all('table')[1].find_all('tr', recursive=False)
    profile['CGPA'] = acads[-2].find_all('td')[5].text.strip()
    subjects = acads[2:-4]
    for subject in subjects:
        subject_data = subject.find_all('td')
        profile['Academic'].append(
            get_subject_template(subject_data[0].text, subject_data[1].text, subject_data[2].text,
                                 subject_data[3].text, subject_data[4].text, subject_data[5].text))

    co_curriculars = co_curricular_row.find_all('table')[1].find_all('tr', recursive=False)[1:-1]

    for co_curricular in co_curriculars:
        co_curricular_data = co_curricular.find_all('td')
        if not co_curricular_data[1].text.startswith('Grade'):
            profile['Co Curricular'].append(
                get_misc_subject_template(co_curricular_data[0].text, co_curricular_data[1].text))
        if not co_curricular_data[3].text.startswith('Grade'):
            profile['Co Curricular'].append(
                get_misc_subject_template(co_curricular_data[2].text, co_curricular_data[3].text))

    co_scholastics = co_scholastic_row.find_all('table')[1].find_all('tr', recursive=False)[2:]

    for co_scholastic in co_scholastics:
        co_scholastic_data = co_scholastic.find_all('td')
        profile['Co Scholastic'].append(
            get_misc_subject_template(co_scholastic_data[0].text, co_scholastic_data[1].text))
        profile['Co Scholastic'].append(
            get_misc_subject_template(co_scholastic_data[2].text, co_scholastic_data[3].text))
    return profile


try:
    log = open("cbse_log.txt", "a")
    with open("cbse_roll_dob.csv", "r") as record_file:
        csv_reader = csv.reader(record_file, delimiter=',')
        for row in csv_reader:
            print(row)
            record[int(row[0].strip())] = datetime.datetime.strptime(row[1], "%Y-%m-%d").date()

    record_file = open("cbse_roll_dob.csv", "a")

    fieldnames = OrderedSet()
    allRows = []

    print('----------------------------------------------')
    temp_dob = START_DOB
    # temp_dob = record[start_roll]

    start_roll = get_next_roll(start_roll, False)

    while START_ROLL <= start_roll <= END_ROLL:
        # temp_dob = record[start_roll]
        log.flush()
        print(start_roll)
        ret, content = attempt(start_roll, temp_dob)

        if ret == -1:
            print("Fatal Error", file=sys.stderr)
            print(start_roll)
            print(temp_dob)
            print('----------------------------------------------')
            sys.exit(-1)

        elif ret == 0:
            log.write("Couldn't get result for %d on %s\n" % (start_roll, temp_dob.strftime("%d/%m/%y")))
            # raise AssertionError("Result not found")
            temp_dob = get_next_date(temp_dob)
            if temp_dob < END_DOB:
                print("DOB for %d out of range" % start_roll)
                start_roll = get_next_roll(start_roll)
                temp_dob = START_DOB
        else:
            print("Successfully got %d for %s" % (start_roll, temp_dob.strftime("%d/%m/%y")))
            log.write("Successfully got %d for %s\n" % (start_roll, temp_dob.strftime("%d/%m/%y")))

            profile = parse_html(content)
            flattened = flatten_json(profile, delim="__")
            fieldnames.update(flattened.keys())
            allRows.append(flattened)

            if start_roll not in record:
                record[start_roll] = str(temp_dob)
                record_file.write("%d,%s\n" % (start_roll, str(temp_dob)))
                record_file.flush()
            start_roll = get_next_roll(start_roll)
            temp_dob = START_DOB

    with open("cbse_data.csv", "w") as file:
        csvwriter = csv.DictWriter(file, fieldnames=fieldnames)
        csvwriter.writeheader()
        for obj in allRows:
            csvwriter.writerow(obj)

except Exception as e:
    # print(record)
    raise AssertionError('Unexpected error occurred')
