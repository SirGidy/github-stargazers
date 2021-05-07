import csv
import asyncio
import httpx
import time
from datetime import datetime, timezone
from time import ctime


class UsernameRepositoryError(ValueError):
    def __init__(self) -> None:
        super().__init__("Argument should be of form username/repository.")


class TooManyRequestsHttpError(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class HTTPError(Exception):
    def __init__(self, status_code: int) -> None:
        super().__init__("{} HTTP.".format(status_code))


class UrlNotFoundError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class GitHub:
    """
        Creates a GitHub instance for listing the stargazers of a given repository
        and checking if a user's full name is in the list of stargazers.
        The constructor requires a string of the following form: `username/repository`,
        both representing the GitHub meaning of them.
    """
    __GITHUB_URL: str = "https://api.github.com/repos/"
    __STARGAZERS_URL_SUFFIX: str = "/stargazers"
    __PER_PAGE_SUFFIX: str = "?per_page=100"
    __ACCEPT_PARAM = 'application/vnd.github.v3.star+json'

    # GitHub API rate limit for un-aunthenticated users
    __API_RATE_LIMIT_PER_HOUR = 60

    # The number of seconds to wait between jobs if expecting to approach the rate limit
    __SEC_BETWEEN_REQUESTS = 60 * 60 / __API_RATE_LIMIT_PER_HOUR

    async_client = httpx.AsyncClient()

    def sleep_gh_rate_limit(self):
        """ 
            Sleep for an amount of time that, if done between GitHub API requests for a full hour,
            will ensure the API rate limit is not exceeded.
        """
        time.sleep(self.__SEC_BETWEEN_REQUESTS + 0.05)

    def extract_next_page_link(self, response):
        """
            Extract the link for the next result page
            from the links header value
        """
        url = ''
        try:
            url = response.links['next']['url']
        except:
            pass
        return url

    def extract_user_and_repo(self, username_and_repository: str):
        try:

            components = username_and_repository.split("/")
            if len(components) != 2:
                raise UsernameRepositoryError()
            for component in components:
                if component == "":
                    raise UsernameRepositoryError()

            return components[0], components[1]
        except Exception as error:
            raise UsernameRepositoryError()

    def get_repository_url(self, username_and_repository) -> str:
        return f'{self.__GITHUB_URL}{username_and_repository}{self.__STARGAZERS_URL_SUFFIX}{self.__PER_PAGE_SUFFIX}'

    async def retrieve_repo_stargazers(self, url: str):
        """
            Parameters
            ---------
            url : str
                The  url to pull stargazers for a repo

            Returns
            -------
            stargazers : List of stargazers in JSON format.

        """
        try:
            list_of_results = []
            while True:
                try:
                    response = await self.github_query_async(url)

                    url = self.extract_next_page_link(response)

                    star_gazers = response.json()
                    list_of_results.extend(star_gazers)
                    # I can un-comment before deployment to ensure will ensure
                    # the API rate limit per hour is not exceeded
                    # self.sleep_gh_rate_limit()
                    if not url:
                        break
                except httpx.RequestError as exc:
                    print(
                        f"An error occurred while requesting {exc.request.url!r} - {exc}."
                    )
                    # TODO : Work on logic to handle 500x error and retry request
                    break
                except httpx.HTTPStatusError as exc:

                    if exc.response.status_code == 403:
                        parsed = exc.response.json()
                        if "message" in parsed:
                            if "API rate limit exceeded" in parsed["message"]:
                                reset_limit = exc.response.headers[
                                    'X-RateLimit-Reset']
                                # We can also opt to sleep  for (reset_limit - seconds_since_epoch)
                                datety = ctime(float(reset_limit))
                                print(
                                    f'API rate limit exceeded. Kindly retry by {datety}'
                                )
                                raise TooManyRequestsHttpError(
                                    f'API rate limit exceeded. Kindly retry by {datety}'
                                )

                    if exc.response.status_code == 404:
                        print(
                            f"An error occurred while requesting {exc.request.url!r} - {exc} "
                        )
                        raise UrlNotFoundError(f'{exc}')

        except (TooManyRequestsHttpError) as ex:
            raise TooManyRequestsHttpError(ex)
        except (UrlNotFoundError) as ex:
            raise UrlNotFoundError(ex)
        except Exception as ex:
            print(ex)
        finally:
            await self.async_client.aclose()
        return list_of_results

        # Another option would be to make initial call, if response header link  has a "next"
        # value, then extract the number of pages / calls(i.e page parameter in the "last" URL)
        # required to pull all stargazers in the repo,  We can then use the use the number of pages
        #  values to construct all URLS to enable us use AsyncClient to execute the requests in
        # parallel on a single thread. I have opted against this route(constructing) despite
        # potential significant performance gains as it could break the system if Github
        # were to change API response header link response format.

        # max_num_of_page = 17 # This value is extacted from the rel="last" URL
        # response = response_await.json()

        # list_of_results = response

        # query_list = [(base_url, q, stargazers_per_page)
        #               for q in range(2, max_num_of_page + 1)]
        # tasks = [
        #     self.github_query_async(*query)
        #     for query in query_list
        # ]
        # completed = await asyncio.gather(*tasks)

    async def github_query_async(self, url: str):
        """
            Fetch stargazers from Github API
            Parameters
            ---------
            url : str
                The url to pull stargazers for a repo

            Returns
            -------
            stargazers : List of stargazersin JSON format.

        """

        try:
            # The async_client uses HTTP connection pooling thereby reuse the underlying
            # TCP connection, instead of recreating one for every single request
            response_await = await self.async_client.get(
                url=url,
                headers={'Accept': self.__ACCEPT_PARAM},
            )
            response_await.raise_for_status()
        except (httpx.RequestError, httpx.HTTPStatusError) as exc:
            raise

        return response_await

    def write_results(self, csv_writer, stargazers=None):
        """
            Write results to csv file on disk.
            Parameters
            ---------
            csv_writer : object
                The csv_writer.
            stargazers : str in JSON format
                The stargazers associated with the user's repo.
            The parameters help to form the filename.
            Returns
            -------
            N/A
        """

        row = [
            stargazers['id'], stargazers['login'], stargazers['url'],
            stargazers['starred_at']
        ]
        csv_writer.writerow(row)