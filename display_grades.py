#!/usr/bin/env python

# based on https://github.com/BenDoan/Infinite-Campus-Grade-Scraper

import cookielib
import mechanize
import config
from BeautifulSoup import BeautifulSoup
from xml.dom import minidom
import utils
import json
from colorama import Fore, Style
from colorama import init
init()

br = mechanize.Browser()


def main():
    with open('grades_db.json', 'r') as db:
        grades = json.loads(db.read())

    headers = []
    spacing_formats = []
    color_formats = []

    headers.append('%')
    spacing_formats.append('{: <7}')
    color_formats.append('\033[0;32m' + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('assignment')
    spacing_formats.append('{: <50}')
    color_formats.append('\033[0;33m' + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('multiplier')
    spacing_formats.append('{: <12}')
    color_formats.append(
        Style.DIM + '\033[2;34m' + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('score')
    spacing_formats.append('{: <8}')
    color_formats.append(Fore.MAGENTA + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('out of')
    spacing_formats.append('{: <8}')
    color_formats.append(Fore.MAGENTA + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('due')
    spacing_formats.append('{: <11}')
    color_formats.append(Style.DIM + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('assigned')
    spacing_formats.append('{: <11}')
    color_formats.append(Style.DIM + '{}' + Style.RESET_ALL + Fore.RESET)

    for class_name in grades:
        class_ = grades[class_name]
        teacher = class_['teacher']
        grade = class_['grade']

        print '\033[4;36m' + class_name + Fore.RESET + Style.RESET_ALL
        print '\033[2;4;36m' + teacher + Fore.RESET + Style.RESET_ALL
        print '\033[34m' + str(grade) + Fore.RESET + Style.RESET_ALL
        print ''

        if grade is 'None':
            print '\n' * 2

            continue

        print Style.BRIGHT + ' '.join(spacing_formats).format(*headers) + Style.RESET_ALL
        print ''

        for section_name in class_['sections']:
            section = class_['sections'][section_name]

            print ('\033[4;31m' + section_name +
                   Style.RESET_ALL).ljust(60) + ' - ' + section['weight'] + '%'

            for assignment in section['assignments']:
                data_columns = assignment

                data_values = [data_columns[key] for key in headers]

                for value, color_format, spacing_format in zip(data_values,
                                                               spacing_formats,
                                                               color_formats):
                    print spacing_format.format(color_format.format(value)),

                print ''
            print ''

        print '\n' * 2


if __name__ == '__main__':
    main()
