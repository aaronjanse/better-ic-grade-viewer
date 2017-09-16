#!/usr/bin/env python

# based on https://github.com/BenDoan/Infinite-Campus-Grade-Scraper

from colorama import Fore, Back, Style
from colorama import init
init()

import cookielib
import mechanize
import config
from BeautifulSoup import BeautifulSoup
from xml.dom import minidom
import utils

br = mechanize.Browser()


def main():
    print('setting up...')
    setup()
    print('logging up...')
    login()

    print('getting grades...')

    headers = []
    spacing_formats = []
    color_formats = []

    headers.append('percent')
    spacing_formats.append('{: <7}')
    color_formats.append('\033[0;32m' + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('assignment_name')
    spacing_formats.append('{: <50}')
    color_formats.append('\033[0;33m' + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('multiplier')
    spacing_formats.append('{: <10}')
    color_formats.append(
        Style.DIM + '\033[2;34m' + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('pts_possible')
    spacing_formats.append('{: <12}')
    color_formats.append(Fore.MAGENTA + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('score')
    spacing_formats.append('{: <5}')
    color_formats.append(Fore.MAGENTA + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('due_date')
    spacing_formats.append('{: <10}')
    color_formats.append(Style.DIM + '{}' + Style.RESET_ALL + Fore.RESET)

    headers.append('assigned_date')
    spacing_formats.append('{: <13}')
    color_formats.append(Style.DIM + '{}' + Style.RESET_ALL + Fore.RESET)

    class_links = get_class_links()
    for classname in class_links:
        link = class_links[classname]
        page = br.open(get_base_url() + link)
        soup = BeautifulSoup(page)
        info_boxes = soup.findAll('a', {'class': 'gridNotPartOfTermGPA'})

        class_info = info_boxes[-1]
        teacher = class_info['title'].split('Teacher: ')[1]

        if class_info.find('span') is not None:
            grade = class_info.find('span').text
        else:
            grade = None

        print classname + ':'
        print teacher
        print grade
        print ''

        if grade is None:
            continue

        print(' '.join(spacing_formats).format(*headers))

        rows = soup.findAll('tr', {'class': 'gridCellNormal'})
        for row in rows:
            if row.find('a') is not None:
                columns = row.findAll('td')

                # assignment_name = columns.pop(0).text
                # due_date = columns.pop(0).text
                # assigned_date = columns.pop(0).text
                # multiplier = columns.pop(0).text
                # pts_possible = columns.pop(0).text
                # score = columns.pop(0).text
                # percent = columns.pop(0).text

                data_columns = {
                    'assignment_name': columns.pop(0).text,
                    'due_date': columns.pop(0).text,
                    'assigned_date': columns.pop(0).text,
                    'multiplier': columns.pop(0).text,
                    'pts_possible': columns.pop(0).text,
                    'score': columns.pop(0).text,
                    'percent': columns.pop(0).text,
                }

                data_values = [data_columns[key] for key in headers]

                for value, color_format, spacing_format in zip(data_values, spacing_formats, color_formats):
                    print spacing_format.format(color_format.format(value)),

                print ''

                # print format_str.format(*data_values)

                # print(row.text)

        print ''
        print ''
        print ''


def get_class_links():
    output = {}
    page = br.open(get_schedule_page_url())
    soup = BeautifulSoup(page)

    for cell in soup.findAll('td'):
        if cell.has_key('class') and cell['class'] == 'scheduleBody':
            link = cell.find('a')
            if link is not None:
                classname = ' '.join(link.find('b').text.split(' ')[1:])
                output[classname] = link['href']

    return output


def setup():
    """general setup commands"""
    # Cookie Jar
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    # Browser options
    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # User-Agent
    br.addheaders = [
        ('User-agent',
         'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]


def login():
    """Logs in to the Infinite Campus at the
    address specified in the config
    """
    br.open(config.login_url)
    br.select_form(nr=0)  # select the first form
    br.form['username'] = config.username
    br.form['password'] = config.password
    br.submit()


def get_base_url():
    """returns the site's base url, taken from the login page url"""
    return config.login_url.split("/campus")[0] + '/campus/'


def get_schedule_page_url():
    """returns the url of the schedule page"""
    school_data = br.open(get_base_url(
    ) + 'portal/portalOutlineWrapper.xsl?x=portal.PortalOutline&contentType=text/xml&lang=en')
    dom = minidom.parse(school_data)

    node = dom.getElementsByTagName('Student')[0]
    person_id = node.getAttribute('personID')
    first_name = node.getAttribute('firstName')
    last_name = node.getAttribute('lastName')

    node = dom.getElementsByTagName('Calendar')[0]
    school_id = node.getAttribute('schoolID')

    node = dom.getElementsByTagName('ScheduleStructure')[0]
    calendar_id = node.getAttribute('calendarID')
    structure_id = node.getAttribute('structureID')
    calendar_name = node.getAttribute('calendarName')

    url = 'portal/portal.xsl?x=portal.PortalOutline&lang=en'
    url += '&personID=' + person_id
    url += '&studentFirstName=' + first_name
    url += '&lastName=' + last_name
    url += '&firstName=' + first_name
    url += '&schoolID=' + school_id
    url += '&calendarID=' + calendar_id
    url += '&structureID=' + structure_id
    url += '&calendarName=' + calendar_name
    url += '&mode=schedule&x=portal.PortalSchedule&x=resource.PortalOptions'

    return utils.url_fix(get_base_url() + url)


if __name__ == '__main__':
    main()
