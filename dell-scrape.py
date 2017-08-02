# -*- coding: utf-8 -*-
import pandas as pd
from lxml import html
import json
import smtplib
import logging

logging.basicConfig(filename='dell-scrape.log', level=logging.WARN)
json_config_file = 'laptop_list.json'
base_url = r'http://downloads.dell.com/published/pages/'
smtp_server = 'mailserver.somewhere'
mail_to = 'to@example.com'
mail_from = 'from@example.com'
mail_subject = 'NY BIOS Opdatering'
mail_template = """From: Dell Scrape Script <{from}>
To: <{to}>
Subject: {subject}

There are BIOS updates for:

{laptop}
"""

# DO NOT CHANGE BELOW

search_url = base_url + 'index.html'
xpath = "//*[@id=\"Drivers-Category.BI-Type.BIOS\"]/table[1]"

try:
    logging.debug('opening config {}'.format(json_config_file))
    with open(json_config_file, 'r') as jfile:
        laptops = json.load(jfile)
except Exception as e:
    logging.exception('failed opening config file {}'.format(json_config_file))

try:
    logging.debug('opening oversigt {}'.format(search_url))
    oversigt = html.parse(search_url)
except Exception as e:
    logging.exception('failed parsing oversigt url {}'.format(search_url))

updated = []


def update_data(laptop, row):
    d = laptops[laptop]
    logging.debug('updating {} existing data {}'.format(laptop, d))
    save = False
    for key in ['Released', 'Version', 'Importance']:
        ny_val = row[key]
        if (key not in d) or (d[key] != ny_val):
            d[key] = ny_val
            laptops[laptop] = d
            save = True
    if save:
        updated.append(laptop)
        with open(json_config_file, 'w') as jfile:
            jfile.write(json.dumps(laptops, indent=4, separators=(',', ': ')))

for laptop in laptops:
    try:
        url = base_url + oversigt.xpath("//a[text()='" + laptop + "']/@href")[0]
        tree = html.parse(url)
        table = tree.xpath(xpath)[0]
        raw_html = html.tostring(table)
        data = pd.read_html(raw_html, header=0)[0]
        row = data.iloc[0]
        update_data(laptop, row)
    except Exception:
        print('Error: fetch info failed for {laptop}'.format(laptop=laptop))

if len(updated) > 0:
    try:
        message = mail_template.format(**{'from': mail_from, 'to': mail_to, 'subject': mail_subject, 'laptop': '\n'.join(updated)})
        smtpObj = smtplib.SMTP(smtp_server)
        smtpObj.sendmail(mail_from, [mail_to], message)
    except smtplib.SMTPException as e:
        print("Error: unable to send email")
