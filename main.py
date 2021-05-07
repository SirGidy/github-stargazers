import asyncio
import csv
import datetime
import httpx

from click import (command, option)
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from github_stargazers.github import GitHub, UsernameRepositoryError, \
    TooManyRequestsHttpError, UrlNotFoundError


@command()
@option("--repo", type=str, help="Repo of interest")
def get_stargazers(repo: str):
    """
        Util that retrieves a list of stargazers for a given GitHub repo.
    """
    try:
        github = GitHub()
        user, repo_name = github.extract_user_and_repo(repo)
        url = github.get_repository_url(repo)
        responses = asyncio.run(github.retrieve_repo_stargazers(url))

        # Format final output returning only values I deem to be required
        # id,login(username),url,starred_at. It can be expanded to include
        # other values.
        if responses:
            formatted = [{
                'id': stargazers['user']['id'],
                'login': stargazers['user']['login'],
                'url': stargazers['user']['url'],
                'starred_at': stargazers['starred_at']
            } for stargazers in responses]

            now = datetime.datetime.now()

            filename = "stargazers-{0}-{1}-{2}.csv".format(
                user, repo_name, now.strftime("%Y%m%d%H%M%S"))

            star_gazers_file = open(filename, 'w')

            # create the csv writer object
            csv_writer = csv.writer(star_gazers_file)

            # headers to the CSV file
            header = ['id', 'login', 'url', 'starred_at']
            csv_writer.writerow(header)

            filewrite = partial(github.write_results, csv_writer)
            with ThreadPoolExecutor() as executor:
                executor.map(filewrite, formatted)
            star_gazers_file.close()
            print(f'{filename} generated successfully')
            return
        print(f'Could not generate stargazers for {repo_name}')
    except (UsernameRepositoryError, TooManyRequestsHttpError,
            UrlNotFoundError) as exception_message:
        print(f' {exception_message}')
        return
    except Exception as exception_message:
        print(f'Error generating file  :  {exception_message}')
        return


if __name__ == "__main__":
    get_stargazers()
