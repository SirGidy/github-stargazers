[![Build Status](https://travis-ci.com/critical-path/py-stargazers.svg?branch=master)](https://travis-ci.com/critical-path/py-stargazers) [![Coverage Status](https://coveralls.io/repos/github/critical-path/py-stargazers/badge.svg)](https://coveralls.io/github/critical-path/py-stargazers)

# stargazers
Stargazers is a python util that retrieves a list of stargazers for a given GitHub repo.


## Dependencies

Stargazers requires Python and the pip package.  It also requires the following libraries for usage and testing.

__Usage__:
- click(https://pypi.org/project/click/)
- httpx(https://www.python-httpx.org/)
- asyncio
- unittest (https://docs.python.org/3/library/unittest.html)

## Setting up  stargazers locally
It is recommended to be installed in a virtual environment with `Python >= 3.6`.

1. Clone or download this repository.

2. `cd` into a repository directory, then create virtual environment.  
  
 ```
 $ python3 -m venv tutorial-env 
 ```
3. Activate virtual environment
   On Windows, run:

   ``` 
   $ <tutorial-env>\Scripts\activate.bat
   ```
   On Unix or MacOS, run:
   
   ``` 
   $ source <tutorial-env>/bin/activate
   ```
   Replace <tutorial-env> with your virtual environment name withouth the <>

4. install requirements Using `sudo`, run `pip` with the `install` command and the `--editable` option.

```
$ pip install requirements.txt
```





## Using stargazers 


To retrieve a list of stargazers associated with a given repo, run `stargazers` with the `--repo` options.

```
 python main.py --repo <repo> 
  e.g <repo>  octocat/hello-world
```
The above command generates a csv file with the name format `stargazers-{0}-{1}-{2}.csv".format(
                user, repo_name, now.strftime("%Y%m%d%H%M%S")` in the directory.


## Note

stargazers makes unauthenticated requests to the GitHub API and is, therefore, subject to rate limits. 