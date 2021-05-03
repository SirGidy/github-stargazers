import datetime
import unittest
import httpx
import asyncio

from github_stargazers.github import GitHub, UsernameRepositoryError
#  extract_user_and_repo, get_repository_url, github_query_async, retrieve_repo_stargazers
from tests.samples import STAR_GAZERS


class TestStarGazers(unittest.TestCase):
    def test_invalid_argument_raises_error(self):
        github = GitHub()
        wrong_arguments = ['foo', 'foo/', '/bar', '/', '//', '']
        for wrong_argument in wrong_arguments:
            with self.assertRaises(UsernameRepositoryError):
                github.extract_user_and_repo(wrong_argument)

    def test_valid_argument_returns_username_and_repo_name(self):
        github = GitHub()
        valid_argument = 'octocat/hello-world'
        user_and_repo = github.extract_user_and_repo(valid_argument)
        self.assertIsInstance(user_and_repo, tuple)
        self.assertEqual(user_and_repo[0], 'octocat')
        self.assertEqual(user_and_repo[1], 'hello-world')

    def test_get_repository_url_returns_valid_url(self):
        github = GitHub()
        repo = 'octocat/hello-world'
        expected_url = 'https://api.github.com/repos/octocat/hello-world/stargazers?per_page=100'
        returned_url = github.get_repository_url(repo)
        self.assertIsNotNone(returned_url)
        self.assertEqual(returned_url, expected_url)

    def test_retrieve_repo_star_gazers_returns_expected_result(self):
        github = GitHub()
        url = 'https://api.github.com/repos/octocat/hello-world/stargazers?per_page=100'
        star_gazers = asyncio.run(github.retrieve_repo_stargazers(url))
        self.assertDictEqual(STAR_GAZERS[0], star_gazers[0])
        all([self.assertIsInstance(x, dict) for x in star_gazers])


if __name__ == '__main__':
    unittest.main()
