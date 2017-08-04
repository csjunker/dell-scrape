# -*- coding: utf-8 -*-
from lxml import html
import json
import smtplib
import logging

logging.basicConfig(filename='dell-scrape.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
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

updated = {}

def update_data(laptop, data):
    save = False
    logging.debug('update_data: {}  {}'.format(laptop, ', '.join(['{}={}'.format(key, data[key]) for key in data])))
    d = laptops[laptop]
    logging.debug('updating {} existing data {}'.format(laptop, d))
    for key in ['Description', 'Released', 'Version', 'Importance', 'Download']:
        ny_val = data[key]
        if (key not in d) or (d[key] != ny_val):
            d[key] = ny_val
            laptops[laptop] = d
            save = True

    if save:
        updated[laptop] = data
        with open(json_config_file, 'w') as jfile:
            jfile.write(json.dumps(laptops, indent=4, separators=(',', ': ')))


def extract_row_data(row):
    return {
        'Description': row[0].xpath('./a/@href')[0],
        'Importance': row[1].xpath('./text()')[0],
        'Version': row[2].xpath('./text()')[0],
        'Released': row[3].xpath('./text()')[0],
        'Download': 'http://downloads.dell.com' + row[5].xpath('./a/@href')[0]
    }


for laptop in laptops:
    try:
        url = base_url + oversigt.xpath("//a[text()='" + laptop + "']/@href")[0]
        logging.debug('main: laptop: {}  url: {}'.format(laptop, url))
        tree = html.parse(url)
        table = tree.xpath(xpath)[0]
        row = table.findall('tr')[1].findall('td')
        data = extract_row_data(row)
        update_data(laptop, data)
    except Exception as e:
        logging.exception('laptop: {}  url: {} '.format(laptop, url))

if len(updated) > 0:
    try:
        laptopmessage = ''
        for laptop in updated:
            laptopmessage += '\n\n{}\n'.format(laptop)
            data = updated[laptop]
            for key in data:
                laptopmessage += '  {}: {}\n'.format(key, data[key])

        message = mail_template.format(**{'from': mail_from, 'to': mail_to, 'subject': mail_subject, 'laptop': laptopmessage})
        smtpObj = smtplib.SMTP(smtp_server)
        smtpObj.sendmail(mail_from, [mail_to], message)
    except smtplib.SMTPException as e:
        logging.exception("Error: unable to send email")
