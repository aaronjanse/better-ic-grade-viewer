#!/usr/bin/env python

# based on https://github.com/BenDoan/Infinite-Campus-Grade-Scraper

import cookielib
import mechanize
import config
from BeautifulSoup import BeautifulSoup
from xml.dom import minidom
import utils

br = mechanize.Browser()


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


def main():
    setup()
    login()
    # page = br.open(get_schedule_page_url())
    page = br.open(get_schedule_page_url())
    soup = BeautifulSoup(page)

    for cell in soup.findAll('td'):
        if cell.has_key('class') and cell['class'] == 'scheduleBody':
            link = cell.find('a')
            if link is not None:
                print link.find('b').text
                print link['href']
                print ''


if __name__ == '__main__':
    main()
