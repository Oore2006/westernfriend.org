import datetime
from django.test import RequestFactory, TestCase
from wagtail.models import Page, Site
from home.models import HomePage
from .models import (
    MagazineDepartmentIndexPage,
    MagazineDepartment,
    MagazineIssue,
    MagazineIndexPage,
    MagazineArticle,
    MagazineTagIndexPage,
)


class MagazineIndexPageTest(TestCase):
    def setUp(self) -> None:
        site_root = Page.objects.get(id=2)

        self.home_page = HomePage(title="Home")
        site_root.add_child(instance=self.home_page)

        Site.objects.all().update(root_page=self.home_page)

        self.magazine_index = MagazineIndexPage(
            title="Magazine",
        )
        self.home_page.add_child(instance=self.magazine_index)

        today = datetime.date.today()

        self.recent_magazine_issue = MagazineIssue(
            title="Issue 1",
            publication_date=today,
        )
        self.magazine_index.add_child(instance=self.recent_magazine_issue)

        number_of_archive_issues = 9
        self.archive_magazine_issues = []

        for i in range(number_of_archive_issues + 1):
            archive_days_ago = datetime.timedelta(days=181 + i)
            archive_magazine_issue = MagazineIssue(
                title=f"Archive issue {i}",
                publication_date=today - archive_days_ago,
            )

            self.magazine_index.add_child(instance=archive_magazine_issue)
            self.archive_magazine_issues.append(archive_magazine_issue)

    def test_get_sitemap_urls(self) -> None:
        """Validate the output of get_sitemap_urls."""

        expected_last_mod = None
        expected_location_contains = "/magazine/"

        sitemap_urls = self.magazine_index.get_sitemap_urls()

        self.assertEqual(len(sitemap_urls), 1)
        self.assertEqual(
            sitemap_urls[0]["lastmod"],
            expected_last_mod,
        )
        self.assertIn(
            expected_location_contains,
            sitemap_urls[0]["location"],
        )

    def test_get_context_recent_issues(self) -> None:
        """Validate the output of get_context."""

        mock_request = RequestFactory().get("/magazine/")

        context = self.magazine_index.get_context(mock_request)

        self.assertEqual(
            list(context["recent_issues"]),
            [self.recent_magazine_issue],
        )

    def test_get_context_archive_issues_without_page_number(self) -> None:
        """Make sure we get the first page when no page number is provided."""

        mock_request = RequestFactory().get("/magazine/")

        context = self.magazine_index.get_context(mock_request)

        number_of_issues_per_page = 8

        self.assertEqual(
            len(list(context["archive_issues"])),
            number_of_issues_per_page,
        )

        self.assertEqual(
            list(context["archive_issues"]),
            self.archive_magazine_issues[:number_of_issues_per_page],
        )

    def test_get_context_archive_issues_with_page_number(self) -> None:
        """Make sure we get the second page of archive issues."""

        mock_request = RequestFactory().get("/magazine/?archive-issues-page=2")

        context = self.magazine_index.get_context(mock_request)

        number_of_issues_per_page = 8
        expected_number_of_issues_on_second_page = 2

        self.assertEqual(
            len(list(context["archive_issues"])),
            expected_number_of_issues_on_second_page,
        )

        self.assertEqual(
            list(context["archive_issues"]),
            self.archive_magazine_issues[number_of_issues_per_page:],
        )

    def test_get_context_archive_issues_with_invalid_numeric_page_number(self) -> None:
        """Make sure we get the first page when an invalid page number is
        provided."""

        mock_request = RequestFactory().get("/magazine/?archive-issues-page=4")

        context = self.magazine_index.get_context(mock_request)  # type: ignore

        number_of_issues_per_page = 8

        self.assertEqual(
            len(list(context["archive_issues"])),
            number_of_issues_per_page,
        )

        self.assertEqual(
            list(context["archive_issues"]),
            self.archive_magazine_issues[:number_of_issues_per_page],
        )

    def test_get_context_archive_issues_with_invalid_non_numeric_page_number(
        self,
    ) -> None:
        """Make sure we get the first page when an invalid page number is
        provided."""

        mock_request = RequestFactory().get("/magazine/?archive-issues-page=foo")

        context = self.magazine_index.get_context(mock_request)

        number_of_issues_per_page = 8

        self.assertEqual(
            len(list(context["archive_issues"])),
            number_of_issues_per_page,
        )

        self.assertEqual(
            list(context["archive_issues"]),
            self.archive_magazine_issues[:number_of_issues_per_page],
        )


class MagazineIssueTest(TestCase):
    def setUp(self) -> None:
        site_root = Page.objects.get(id=2)

        self.home_page = HomePage(title="Home")
        site_root.add_child(instance=self.home_page)

        Site.objects.all().update(root_page=self.home_page)

        self.magazine_index = MagazineIndexPage(title="Magazine")
        self.home_page.add_child(instance=self.magazine_index)

        self.magazine_issue = MagazineIssue(
            title="Issue 1",
            issue_number=1,
            publication_date="2020-01-01",
        )

        self.magazine_department_index = MagazineDepartmentIndexPage(
            title="Departments",
        )
        self.magazine_index.add_child(instance=self.magazine_department_index)
        self.magazine_department_one = MagazineDepartment(
            title="Department 1",
        )
        self.magazine_department_two = MagazineDepartment(
            title="Department 2",
        )

        self.magazine_department_index.add_child(instance=self.magazine_department_one)
        self.magazine_department_index.add_child(instance=self.magazine_department_two)
        self.magazine_index.add_child(instance=self.magazine_issue)
        self.magazine_article_one = self.magazine_issue.add_child(
            instance=MagazineArticle(
                title="Article 1",
                department=self.magazine_department_two,
                is_featured=True,
            ),
        )
        self.magazine_article_two = self.magazine_issue.add_child(
            instance=MagazineArticle(
                title="Article 2",
                department=self.magazine_department_one,
                is_featured=False,
            ),
        )

    def test_featured_articles(self) -> None:
        """Test that the featured_articles property returns the correct
        articles."""
        self.assertEqual(
            list(self.magazine_issue.featured_articles),
            [self.magazine_article_one],
        )

    def test_articles_by_department(self) -> None:
        """Test that the articles_by_department property returns the correct
        articles."""
        self.assertEqual(
            list(self.magazine_issue.articles_by_department),
            [
                self.magazine_article_two,
                self.magazine_article_one,
            ],
        )

    def test_publication_end_date(self) -> None:
        """Test that the publication_end_date property returns the correct
        date."""
        self.assertEqual(
            self.magazine_issue.publication_end_date,
            datetime.date(2020, 2, 1),
        )

    def test_get_sitemap_urls(self) -> None:
        """Validate the output of get_sitemap_urls."""

        expected_last_mod = None
        expected_location_contains = "/magazine/issue-1/"

        sitemap_urls = self.magazine_issue.get_sitemap_urls()

        self.assertEqual(len(sitemap_urls), 1)
        self.assertEqual(
            sitemap_urls[0]["lastmod"],
            expected_last_mod,
        )
        self.assertIn(
            expected_location_contains,
            sitemap_urls[0]["location"],
        )


class MagazineTagIndexPageTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.root = Site.objects.get(is_default_site=True).root_page

        # Create a MagazineIndexPage
        self.magazine_index = MagazineIndexPage(title="Magazine")
        self.root.add_child(instance=self.magazine_index)

        # Create a page of MagazineTagIndexPage type
        self.magazine_tag_index_page = MagazineTagIndexPage(title="Tag Index")
        self.magazine_index.add_child(instance=self.magazine_tag_index_page)

        # Create a MagazineDepartmentIndexPage
        self.department_index = MagazineDepartmentIndexPage(title="Departments")
        self.magazine_index.add_child(instance=self.department_index)

        # Create some MagazineDepartments
        self.department1 = MagazineDepartment(
            title="Department 1",
        )
        self.department2 = MagazineDepartment(
            title="Department 2",
        )

        self.department_index.add_child(instance=self.department1)
        self.department_index.add_child(instance=self.department2)

        # Create some MagazineArticles with tags
        self.article1 = MagazineArticle(
            title="Article 1",
            department=self.department1,
        )
        self.article2 = MagazineArticle(
            title="Article 2",
            department=self.department2,
        )
        self.article3 = MagazineArticle(
            title="Article 3",
            department=self.department2,
        )

        python_tag = "Python"
        django_tag = "Django"

        self.article1.tags.add(python_tag)
        self.article2.tags.add(python_tag)
        self.article3.tags.add(django_tag)

        self.magazine_index.add_child(instance=self.article1)
        self.magazine_index.add_child(instance=self.article2)
        self.magazine_index.add_child(instance=self.article3)

        MagazineArticle.objects.all()

    def test_get_context(self) -> None:
        # Create a mock request with 'tag' as a GET parameter
        request = self.factory.get("/magazine/tag-index/?tag=Python")

        # Call the get_context method
        context = self.magazine_tag_index_page.get_context(request)

        # Check that the context includes the articles tagged with 'Python'
        self.assertEqual(
            list(context["articles"]),
            [self.article1, self.article2],
        )

        # Check that the context doesn't include articles tagged with 'Django'
        self.assertNotIn(
            self.article3,
            context["articles"],
        )


class MagazineDepartmentIndexPageTest(TestCase):
    def setUp(self) -> None:
        self.factory = RequestFactory()
        self.root = Site.objects.get(is_default_site=True).root_page

        # Create a MagazineIndexPage
        self.magazine_index = MagazineIndexPage(title="Magazine")
        self.root.add_child(instance=self.magazine_index)

        # Create a MagazineDepartmentIndexPage
        self.department_index = MagazineDepartmentIndexPage(title="Department Index")
        self.magazine_index.add_child(instance=self.department_index)

        # Create some MagazineDepartments
        self.department1 = MagazineDepartment(title="Department 1")
        self.department2 = MagazineDepartment(title="Department 2")

        self.department_index.add_child(instance=self.department1)
        self.department_index.add_child(instance=self.department2)

    def test_get_context(self) -> None:
        # Create a mock request
        request = self.factory.get("/")

        # Call the get_context method
        context = self.department_index.get_context(request)

        # Check that the context includes the departments
        self.assertQuerySetEqual(  # type: ignore
            context["departments"],
            MagazineDepartment.objects.all(),
            transform=lambda x: x,  # Transform the objects to compare them directly
            ordered=False,  # The order of the results is not important
        )
