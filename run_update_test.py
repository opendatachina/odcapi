#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import unittest
import tempfile
import datetime
from httmock import response, HTTMock
from mock import Mock
from time import time
from re import match

import logging
root_logger = logging.getLogger()
root_logger.disabled = True

class FakeResponse:
    def __init__(self, text):
        self.text = text

class RunUpdateTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['DATABASE_URL'] = 'postgres://postgres@localhost/civic_json_worker_test'
        os.environ['SECRET_KEY'] = '123456'
        os.environ['MEETUP_KEY'] = 'abcdef'

        from app import db

        self.db = db
        self.db.create_all()

        import run_update
        run_update.github_throttling = False

    def tearDown(self):
        self.db.session.close()
        self.db.drop_all()

    def mock_rss_response(self):
        import urllib2

        rss_file=open('blog.xml')
        rss_content = rss_file.read()
        rss_file.close()
        urllib2.urlopen = Mock()
        urllib2.urlopen.return_value.read = Mock(return_value=rss_content)
        return urllib2.urlopen

    def response_content(self, url, request):
        import run_update

        if url.geturl() == 'http://example.com/cfa-projects.csv':
            return response(200, '''name,description,link_url,code_url,type,categories\n,"Thing for ""stuff"".",,https://github.com/codeforamerica/cityvoice,web service,"community engagement, housing"\nSouthBendVoices,,,https://github.com/codeforamerica/cityvoice,,''')

        elif "docs.google.com" in url:
            return response(200, u'''name,website,events_url,rss,projects_list_url\nCöde for Ameriça,http://codeforamerica.org,http://www.meetup.com/events/Code-For-Charlotte/,http://www.codeforamerica.org/blog/feed/,http://example.com/cfa-projects.csv\nCode for America (2),,,,https://github.com/codeforamerica\nCode for America (3),,,,https://www.github.com/orgs/codeforamerica'''.encode('utf8'))

        elif url.geturl() == 'https://api.github.com/repos/codeforamerica/cityvoice':
            return response(200, '''{ "id": 10515516, "name": "cityvoice", "owner": { "login": "codeforamerica", "avatar_url": "https://avatars.githubusercontent.com/u/337792", "html_url": "https://github.com/codeforamerica", "type": "Organization"}, "html_url": "https://github.com/codeforamerica/cityvoice", "description": "A place-based call-in system for gathering and sharing community feedback",  "url": "https://api.github.com/repos/codeforamerica/cityvoice", "contributors_url": "https://api.github.com/repos/codeforamerica/cityvoice/contributors", "created_at": "2013-06-06T00:12:30Z", "updated_at": "2014-02-21T20:43:16Z", "pushed_at": "2014-02-21T20:43:16Z", "homepage": "http://www.cityvoiceapp.com/", "stargazers_count": 10, "watchers_count": 10, "language": "Ruby", "forks_count": 12, "open_issues": 37 }''', {'last-modified': datetime.datetime.strptime('Fri, 15 Nov 2013 00:08:07 GMT',"%a, %d %b %Y %H:%M:%S GMT")})

        elif url.geturl() == 'https://api.github.com/repos/codeforamerica/cityvoice/contributors':
            return response(200, '''[ { "login": "daguar", "avatar_url": "https://avatars.githubusercontent.com/u/994938", "url": "https://api.github.com/users/daguar", "html_url": "https://github.com/daguar", "contributions": 518 } ]''')

        elif url.geturl() == 'https://api.github.com/repos/codeforamerica/cityvoice/stats/participation':
            return response(200, '''{ "all": [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 23, 9, 4, 0, 77, 26, 7, 17, 53, 59, 37, 40, 0, 47, 59, 55, 118, 11, 8, 3, 3, 30, 0, 1, 1, 4, 6, 1, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1 ], "owner": [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ] }''')

        elif url.geturl() == 'https://api.github.com/repos/codeforamerica/cityvoice/issues':
            return response(200, ''' [ {"html_url": "https://github.com/codeforamerica/cityvoice/issue/210","title": "Important cityvoice issue", "labels": [ ], "body" : "WHATEVER"} ] ''', {'ETag': '8456bc53d4cf6b78779ded3408886f82'})

        elif url.geturl() == 'https://api.github.com/users/daguar':
            return response(200, '''{ "login": "daguar", "avatar_url": "https://gravatar.com/avatar/whatever", "html_url": "https://github.com/daguar", "name": "Dave Guarino", "company": "", "blog": null, "location": "Oakland, CA", "email": "dave@codeforamerica.org",  }''')

        elif url.geturl() == 'https://api.github.com/users/codeforamerica/repos':
            return response(200, '''[{ "id": 10515516, "name": "cityvoice", "owner": { "login": "codeforamerica", "avatar_url": "https://avatars.githubusercontent.com/u/337792", "html_url": "https://github.com/codeforamerica", "type": "Organization"}, "html_url": "https://github.com/codeforamerica/cityvoice", "description": "A place-based call-in system for gathering and sharing community feedback",  "url": "https://api.github.com/repos/codeforamerica/cityvoice", "contributors_url": "https://api.github.com/repos/codeforamerica/cityvoice/contributors", "created_at": "2013-06-06T00:12:30Z", "updated_at": "2014-02-21T20:43:16Z", "pushed_at": "2014-02-21T20:43:16Z", "homepage": "http://www.cityvoiceapp.com/", "stargazers_count": 10, "watchers_count": 10, "language": "Ruby", "forks_count": 12, "open_issues": 37 }]''', headers=dict(Link='<https://api.github.com/user/337792/repos?page=2>; rel="next", <https://api.github.com/user/337792/repos?page=2>; rel="last"'))

        elif url.geturl() == 'https://api.github.com/user/337792/repos?page=2':
            return response(200, '''[ ]''', headers=dict(Link='<https://api.github.com/user/337792/repos?page=1>; rel="prev", <https://api.github.com/user/337792/repos?page=1>; rel="first"'))

        elif match(r'https:\/\/api\.meetup\.com\/2\/events\?status=past,upcoming&format=json&group_urlname=Code-For-Charlotte&key=', url.geturl()):
            events_file=open('meetup_events.json')
            events_content = events_file.read()
            events_file.close()
            return response(200, events_content)

        elif url.geturl() == 'http://www.codeforamerica.org/blog/feed/' or match(r'http:\/\/.+\.rss', url.geturl()):
            stories_file=open('blog.xml')
            stories_content = stories_file.read()
            stories_file.close()
            return response(200, stories_content)

        else:
            raise Exception('Asked for unknown URL ' + url.geturl())

    def test_import(self):
        ''' Add one sample organization with two projects and issues, verify that it comes back.
        '''
        with HTTMock(self.response_content):
            import run_update
            run_update.main(org_sources="test_org_sources.csv")

        self.db.session.flush()

        from app import Organization, Project, Issue

        # check for the one organization
        filter = Organization.name == u'Cöde for Ameriça'
        organization = self.db.session.query(Organization).filter(filter).first()
        self.assertIsNotNone(organization)
        self.assertEqual(organization.name,u'Cöde for Ameriça')

        # check for the one project
        filter = Project.name == 'SouthBendVoices'
        project = self.db.session.query(Project).filter(filter).first()
        self.assertIsNotNone(project)
        self.assertEqual(project.name,'SouthBendVoices')

        # check for the other project
        filter = Project.name == 'cityvoice'
        project = self.db.session.query(Project).filter(filter).first()
        self.assertIsNotNone(project)
        self.assertEqual(project.name,'cityvoice')

        # check for cityvoice project's issues
        filter = Issue.project_id == project.id
        issue = self.db.session.query(Issue).filter(filter).first()
        self.assertIsNotNone(issue)
        self.assertEqual(issue.title, 'Important cityvoice issue')

    def test_main_with_good_new_data(self):
        ''' When current organization data is not the same set as existing, saved organization data,
            the new organization, its project, and events should be saved. The out of date
            organization, its project and event should be deleted.
        '''
        from factories import OrganizationFactory, ProjectFactory, EventFactory, IssueFactory

        old_organization = OrganizationFactory(name='Old Organization')
        old_project = ProjectFactory(name='Old Project', organization_name='Old Organization')
        old_event = EventFactory(name='Old Event', organization_name='Old Organization')
        old_issue = IssueFactory(title='Old Issue', project_id=1)
        self.db.session.flush()

        self.mock_rss_response()

        with HTTMock(self.response_content):
            import run_update
            run_update.main(org_sources="test_org_sources.csv")

        self.db.session.flush()

        from app import Organization, Project, Event, Issue

        # make sure old org is no longer there
        filter = Organization.name == 'Old Organization'
        organization = self.db.session.query(Organization).filter(filter).first()
        self.assertIsNone(organization)

        # make sure old project is no longer there
        filter = Project.name == 'Old Project'
        project = self.db.session.query(Project).filter(filter).first()
        self.assertIsNone(project)

        # make sure the old issue is no longer there
        filter = Issue.title == 'Old Issue'
        issue = self.db.session.query(Issue).filter(filter).first()
        self.assertIsNone(issue)

        # make sure old event is no longer there
        filter = Event.name == 'Old Event'
        event = self.db.session.query(Event).filter(filter).first()
        self.assertIsNone(event)


        # check for the one organization
        filter = Organization.name == u'Cöde for Ameriça'
        organization = self.db.session.query(Organization).filter(filter).first()
        self.assertEqual(organization.name, u'Cöde for Ameriça')

        # check for the one project
        filter = Project.name == 'SouthBendVoices'
        project = self.db.session.query(Project).filter(filter).first()
        self.assertEqual(project.name,'SouthBendVoices')

        # check for the one issue
        filter = Issue.title == 'Important cityvoice issue'
        issue = self.db.session.query(Issue).filter(filter).first()
        self.assertEqual(issue.title, 'Important cityvoice issue')

        # check for events
        filter = Event.name.in_(['Organizational meeting',
                                 'Code Across: Launch event',
                                 'Brigade Ideation (Brainstorm and Prototyping) Session.'])
        events = self.db.session.query(Event).filter(filter).all()

        first_event = events.pop(0)
        # Thu, 16 Jan 2014 19:00:00 -05:00
        self.assertEqual(first_event.utc_offset, -5 * 3600)
        self.assertEqual(first_event.start_time_notz, datetime.datetime(2014, 1, 16, 19, 0, 0))
        self.assertEqual(first_event.name, 'Organizational meeting')

        second_event = events.pop(0)
        # Thu, 20 Feb 2014 18:30:00 -05:00
        self.assertEqual(first_event.utc_offset, -5 * 3600)
        self.assertEqual(second_event.start_time_notz, datetime.datetime(2014, 2, 20, 18, 30, 0))
        self.assertEqual(second_event.name, 'Code Across: Launch event')

        third_event = events.pop(0)
        # Wed, 05 Mar 2014 17:30:00 -05:00
        self.assertEqual(first_event.utc_offset, -5 * 3600)
        self.assertEqual(third_event.start_time_notz, datetime.datetime(2014, 3, 5, 17, 30, 0))
        self.assertEqual(third_event.name, 'Brigade Ideation (Brainstorm and Prototyping) Session.')

    def test_main_with_missing_projects(self):
        ''' When github returns a 404 when trying to retrieve project data,
            an error message should be logged.
        '''
        def response_content(url, request):
            import run_update

            if url.geturl() == 'http://example.com/cfa-projects.csv':
                return response(200, '''name,description,link_url,code_url,type,categories\n,,http://google.com,https://github.com/codeforamerica/cityvoice,,''')

            elif "docs.google.com" in url:
                return response(200, '''name,website,events_url,rss,projects_list_url\nCode for America,,,,http://example.com/cfa-projects.csv''')

            elif url.geturl() == 'https://api.github.com/repos/codeforamerica/cityvoice':
                return response(404, '''Not Found!''', {'ETag': '8456bc53d4cf6b78779ded3408886f82'})

            elif url.geturl() == 'https://api.github.com/repos/codeforamerica/cityvoice/issues':
                return response(404, '''Not Found!''', {'ETag': '8456bc53d4cf6b78779ded3408886f82'})

            else:
                raise Exception('Asked for unknown URL ' + url.geturl())

        import logging
        logging.error = Mock()

        with HTTMock(response_content):
            import run_update
            run_update.main(org_sources="test_org_sources.csv")

        logging.error.assert_called_with('https://api.github.com/repos/codeforamerica/cityvoice doesn\'t exist.')

    def test_main_with_github_errors(self):
        ''' When github returns a non-404 error code, an IOError should be raised.
        '''
        def response_content(url, request):
            import run_update

            if url.geturl() == 'http://example.com/cfa-projects.csv':
                return response(200, '''name,description,link_url,code_url,type,categories\n,,,https://github.com/codeforamerica/cityvoice,,''')

            elif "docs.google.com" in url:
                return response(200, '''name,website,events_url,rss,projects_list_url\nCode for America,,,,http://example.com/cfa-projects.csv''')

            elif url.geturl() == 'https://api.github.com/repos/codeforamerica/cityvoice':
                return response(422, '''Unprocessable Entity''')

        with HTTMock(response_content):
            import run_update
            self.assertFalse(run_update.github_throttling)
            with self.assertRaises(IOError):
                run_update.main(org_sources="test_org_sources.csv")

    def test_main_with_weird_organization_name(self):
        ''' When an organization has a weird name, ...
        '''
        def response_content(url, request):
            import run_update

            if "docs.google.com" in url:
                return response(200, '''name\nCode_for-America''')
            else:
                raise Exception('Asked for unknown URL ' + url.geturl())

        import logging
        logging.error = Mock()

        self.mock_rss_response()

        with HTTMock(response_content):
            import run_update
            run_update.main(org_sources="test_org_sources.csv")
            from app import Error
            errors = self.db.session.query(Error).all()
            for error in errors:
                self.assertTrue("ValueError" in error.error)
            self.assertEqual(self.db.session.query(Error).count(),1)


        from app import Organization

        # Make sure no organizations exist
        orgs_count = self.db.session.query(Organization).count()
        self.assertEqual(orgs_count, 0)

    def test_main_with_bad_organization_name(self):
      ''' When an org has a invalid name, test that it gets skipped and an error is added to the db
      '''

      def response_content(url, request):
          return response(200, '''name\nCode#America\nCode?America\nCode/America\nCode for America''')

      with HTTMock(response_content):
          import run_update
          run_update.main(org_sources="test_org_sources.csv")
          from app import Error
          errors = self.db.session.query(Error).all()
          for error in errors:
              self.assertTrue("ValueError" in error.error)
          self.assertEqual(self.db.session.query(Error).count(),3)

      # Make sure one good organization exists
      from app import Organization
      orgs_count = self.db.session.query(Organization).count()
      self.assertEqual(orgs_count, 1)

    def test_main_with_bad_events_url(self):
        ''' When an organization has a badly formed events url is passed, no events are saved
        '''
        def response_content(url, request):
            import run_update

            if "docs.google.com" in url:
                return response(200, '''name,events_url\nCode for America,http://www.meetup.com/events/foo-%%%''')

            else:
                raise Exception('Asked for unknown URL ' + url.geturl())

        import logging
        logging.error = Mock()

        with HTTMock(response_content):
            import run_update
            run_update.main(org_sources="test_org_sources.csv")

        logging.error.assert_called_with('Code for America does not have a valid events url')

        from app import Event

        # Make sure no events exist
        events_count = self.db.session.query(Event).count()
        self.assertEqual(events_count, 0)

    def test_main_with_non_existant_meetup(self):
        ''' When meetup returns a 404 for an organization's events url, an error
            message should be logged
        '''
        def response_content(url, request):
            import run_update

            if "docs.google.com" in url:
                return response(200, '''name,events_url\nCode for America,http://www.meetup.com/events/Code-For-Charlotte''')

            if 'api.meetup.com' in url:
                return response(404, '''Not Found!''')

            else:
                raise Exception('Asked for unknown URL ' + url.geturl())

        import logging

        logging.error = Mock()
        self.mock_rss_response()

        with HTTMock(response_content):
            import run_update
            run_update.main(org_sources="test_org_sources.csv")

        logging.error.assert_called_with('Code for America\'s meetup page cannot be found')

    def test_main_with_stories(self):
        '''
        Test that two most recent blog posts are in the db.
        '''
        self.mock_rss_response()

        from factories import OrganizationFactory
        organization = OrganizationFactory(name='Code for America')

        with HTTMock(self.response_content):
            import run_update as ru
            for story_info in ru.get_stories(organization):
                ru.save_story_info(self.db.session, story_info)

        self.db.session.flush()

        from app import Story

        stories_count = self.db.session.query(Story).count()
        self.assertEqual(stories_count, 2)

        stories = self.db.session.query(Story).all()
        self.assertEqual(stories[0].title, "Four Great Years")
        self.assertEqual(stories[1].title, "Open, transparent Chattanooga")

    def test_github_throttling(self):
        '''
        Test that when GitHub throttles us, we skip updating projects and record an error.
        '''

        def response_content(url, request):
            if url.netloc == 'docs.google.com':
                return response(200, '''name,projects_list_url\nCode for San Francisco,http://github.com/codeforsanfrancisco''')
            if url.netloc == 'api.github.com' and url.path == '/users/codeforsanfrancisco/repos':
                return response(200, '''[{ "id": 10515516, "name": "cityvoice", "owner": { "login": "codeforamerica", "avatar_url": "https://avatars.githubusercontent.com/u/337792", "html_url": "https://github.com/codeforamerica", "type": "Organization"}, "html_url": "https://github.com/codeforamerica/cityvoice", "description": "A place-based call-in system for gathering and sharing community feedback",  "url": "https://api.github.com/repos/codeforamerica/cityvoice", "contributors_url": "https://api.github.com/repos/codeforamerica/cityvoice/contributors", "created_at": "2013-06-06T00:12:30Z", "updated_at": "2014-02-21T20:43:16Z", "pushed_at": "2014-02-21T20:43:16Z", "homepage": "http://www.cityvoiceapp.com/", "stargazers_count": 10, "watchers_count": 10, "language": "Ruby", "forks_count": 12, "open_issues": 37 }]''', headers=dict(Link='<https://api.github.com/user/337792/repos?page=2>; rel="next", <https://api.github.com/user/337792/repos?page=2>; rel="last"'))
            if url.netloc == 'api.github.com' and url.path == '/user/337792/repos':
                return response(200, '''[{"id": 12120917, "name": "beyondtransparency", "description": "Code for America's new book - Beyond Transparency :closed_book:", "homepage": "http://beyondtransparency.org", "html_url": "https://github.com/codeforamerica/beyondtransparency"}]''')
            if url.netloc == 'api.github.com':
                return response(403, "", {"x-ratelimit-remaining" : 0})

        with HTTMock(response_content):
            import run_update
            run_update.main(org_sources="test_org_sources.csv")

        from app import Project
        projects = self.db.session.query(Project).all()
        for project in projects:
            self.assertIsNone(project.github_details)

        from app import Organization
        org_count = self.db.session.query(Organization).count()
        self.assertEqual(org_count, 1)

        from app import Error
        error = self.db.session.query(Error).first()
        self.assertEqual(error.error, "IOError: We done got throttled by GitHub")

    def test_csv_sniffer(self):
        '''
        Testing weird csv dialects we've encountered
        '''
        from factories import OrganizationFactory
        philly = OrganizationFactory(name='Code for Philly')
        gdocs = OrganizationFactory(projects_list_url="http://www.gdocs.com/projects.csv")

        def response_content(url, request):
            if url.netloc == 'www.civicorganization1.com':
                return response(200, '''"name","description","link_url","code_url","type","categories"\r\n"OpenPhillyGlobe","\"Google Earth for Philadelphia\" with open source and open transit data.","http://cesium.agi.com/OpenPhillyGlobe/","","",""''')
            if url.netloc == 'www.gdocs.com':
                return response(200, '''name,description,link_url,code_url,type,categories\r\nHack Task Aggregator,"Web application to aggregate tasks across projects that are identified for ""hacking"".",http://open-austin.github.io/hack-task-aggregator/public/index.html,,web service,"project management, civic hacking"''')

        with HTTMock(response_content):
            import run_update
            projects = run_update.get_projects(philly)
            self.assertEqual(projects[0]['name'], "OpenPhillyGlobe")
            self.assertEqual(projects[0]['description'], 'Google Earth for Philadelphia" with open source and open transit data."')

            projects = run_update.get_projects(gdocs)
            self.assertEqual(projects[0]['name'], "Hack Task Aggregator")
            self.assertEqual(projects[0]['description'], 'Web application to aggregate tasks across projects that are identified for "hacking".')

    def test_non_github_projects(self):
        ''' Test that non github and non code projects get last_updated timestamps.
        '''
        from factories import OrganizationFactory
        whatever = OrganizationFactory(name='Whatever')
        gdocs = OrganizationFactory(projects_list_url="http://www.gdocs.com/projects.csv")

        def response_content(url, request):
            if url.netloc == 'www.civicorganization6.com':
                return response(200, '''"name","description","link_url","code_url","type","categories"\r\n"OpenPhillyGlobe","\"Google Earth for Philadelphia\" with open source and open transit data.","http://cesium.agi.com/OpenPhillyGlobe/","http://google.com","",""''')
            if url.netloc == 'www.gdocs.com':
                return response(200, '''name,description,link_url,code_url,type,categories\nHack Task Aggregator,"Web application to aggregate tasks across projects that are identified for ""hacking"".",,,web service,"project management, civic hacking"''')


        with HTTMock(response_content):
            import run_update
            projects = run_update.get_projects(whatever)
            self.assertEqual(projects[0]['name'], "OpenPhillyGlobe")
            self.assertEqual(projects[0]['last_updated'], datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z"))

            projects = run_update.get_projects(gdocs)
            self.assertEqual(projects[0]['name'], "Hack Task Aggregator")
            self.assertEqual(projects[0]['last_updated'], datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z"))

    def test_org_sources_csv(self):
        '''Test that there is a csv file with links to lists of organizations
        '''
        import run_update
        self.assertTrue(os.path.exists(run_update.ORG_SOURCES))

    def test_utf8_noncode_projects(self):
        ''' Test that utf8 project descriptions match exisiting projects.
        '''
        from factories import OrganizationFactory, ProjectFactory


        philly = OrganizationFactory(name='Code for Philly', projects_list_url="http://codeforphilly.org/projects.csv")
        old_project = ProjectFactory(name='Philly Map of Shame', organization_name='Code for Philly', description=u'PHL Map of Shame is a citizen-led project to map the impact of the School Reform Commission\u2019s \u201cdoomsday budget\u201d on students and parents. We will visualize complaints filed with the Pennsylvania Department of Education.', categories='Education, CivicEngagement', type='', link_url='http://phillymapofshame.org')
        self.db.session.flush()

        def response_content(url, request):
            if url.geturl() == 'http://codeforphilly.org/projects.csv':
                return response(200, '''"name","description","link_url","code_url","type","categories"\r\n"Philly Map of Shame","PHL Map of Shame is a citizen-led project to map the impact of the School Reform Commission\xe2\x80\x99s \xe2\x80\x9cdoomsday budget\xe2\x80\x9d on students and parents. We will visualize complaints filed with the Pennsylvania Department of Education.","http://phillymapofshame.org","","","Education, CivicEngagement"''')
            
        with HTTMock(response_content):
            import run_update
            projects = run_update.get_projects(philly)

            assert projects[0]['last_updated'] == None

    def test_issue_paging(self):
        ''' test that issues are following page links '''
        from factories import OrganizationFactory, ProjectFactory

        organization = OrganizationFactory(name='Code for America', projects_list_url="http://codeforamerica.org/projects.csv")
        project = ProjectFactory(organization_name='Code for America',code_url='https://github.com/TESTORG/TESTPROJECT')

        def response_content(url, request):
            if url.geturl() == 'https://api.github.com/repos/TESTORG/TESTPROJECT/issues':
                content = '''[{"number": 2,"title": "TEST TITLE 2","body": "TEST BODY 2","labels": [], "html_url":""}]'''
                headers = {"Link": '<https://api.github.com/repos/TESTORG/TESTPROJECT/issues?page=2>"; rel="next"','ETag':'TEST ETAG'}
                return response(200, content, headers)

            elif url.geturl() == 'https://api.github.com/repos/TESTORG/TESTPROJECT/issues?page=2':
                content = '''[{"number": 2,"title": "TEST TITLE 2","body": "TEST BODY 2","labels": [], "html_url":""}]'''
                return response(200, content)


        with HTTMock(response_content):
            import run_update
            issues, labels = run_update.get_issues(organization.name)
            assert (len(issues) == 2)

    def test_project_list_without_all_columns(self):
        ''' Get a project list that doesn't have all the columns.
            Don't die.
        '''
        from app import Project
        from factories import OrganizationFactory, ProjectFactory

        organization = OrganizationFactory(name="TEST ORG", projects_list_url="http://www.gdocs.com/projects.csv")
        project = ProjectFactory(organization_name="TEST ORG", name="TEST PROJECT2", description="TEST DESCRIPTION 2", link_url="http://testurl.org")
        self.db.session.flush()

        def response_content(url, request):
            if url.netloc == 'www.gdocs.com':
                return response(200, '''name,description,link_url,code_url\nTEST PROJECT,TEST DESCRIPTION,http://google.com,https://github.com/testorg/testproject\nTEST PROJECT2,TEST DESCRIPTION2,http://google.com,http://whatever.com/testproject''')
            elif url.netloc == 'api.github.com':
                return response(200, '''{ "id": 10515516, "name": "cityvoice", "owner": { "login": "codeforamerica", "avatar_url": "https://avatars.githubusercontent.com/u/337792", "html_url": "https://github.com/codeforamerica", "type": "Organization"}, "html_url": "https://github.com/codeforamerica/cityvoice", "description": "A place-based call-in system for gathering and sharing community feedback",  "url": "https://api.github.com/repos/codeforamerica/cityvoice", "contributors_url": "https://api.github.com/repos/codeforamerica/cityvoice/contributors", "created_at": "2013-06-06T00:12:30Z", "updated_at": "2014-02-21T20:43:16Z", "pushed_at": "2014-02-21T20:43:16Z", "homepage": "http://www.cityvoiceapp.com/", "stargazers_count": 10, "watchers_count": 10, "language": "Ruby", "forks_count": 12, "open_issues": 37 }''', {'last-modified': datetime.datetime.strptime('Fri, 15 Nov 2013 00:08:07 GMT',"%a, %d %b %Y %H:%M:%S GMT")})
            elif url.netloc == 'whatever.com':
                return response(200, '''"name","description","link_url","code_url"\n"TEST PROJECT2","TEST DESCRIPTION 2","http://testurl.org",""''')

        with HTTMock(response_content):
            import run_update
            projects = run_update.get_projects(organization)
            assert len(projects) == 2

    def test_missing_last_updated(self):
        ''' In rare cases, a project will be in the db without a last_updated date
            Remove a project's last_updated and try and update it.
        '''
        from app import Project
        import run_update

        with HTTMock(self.response_content):
            run_update.main(org_name=u"C\xf6de for Ameri\xe7a", org_sources="test_org_sources.csv")
            self.db.session.query(Project).update({"last_updated":None})
            run_update.main(org_name=u"C\xf6de for Ameri\xe7a", org_sources="test_org_sources.csv")


if __name__ == '__main__':
    unittest.main()
