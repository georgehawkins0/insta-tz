# insta-tz
Get analysis of instagram user post time from a cli based OSINT application.

<p align="center">
<img src="img/insta-tz.png" width=100/>
</p>

# Table of contents

- [Installation](#installation)
- [Start](#start)
- [Usage](#usage)
- [About / Further reading](#about)


# Installation


Clone the github repo
```
$ git clone https://github.com/georgehawkins0/insta-tz.git
```
Change Directory

```
$ cd insta-tz
```
Install requirements
```
$ python3 -m pip install -r requirements.txt
```

# Start
To use this tool, you will need an instagram account. If the users you wish to analyse are private, this instagram account needs to be following them. 

You need to add login credentials for the account you wish to do the crawling from in creds/creds.yml


# Usage

## Example usage

1. Analyse user @github

        $ tz.py --target github


2. Analyse post time of @github, but only crawl the 250 most recent posts

        $ tz.py --target github --limit 250

## Args list


```
usage: tz.py [-h] [-t TARGET] [-l LIMIT] [-p]

Analysis of user post time.

optional arguments:
  -h, --help            show this help message and exit
  -t TARGET, --target TARGET
                        Target username
  -l LIMIT, --limit LIMIT
                        Post limit to crawl.
  -p, --percent         Display percentages on the hour frequency graph
```


# Example Output
```
        ██╗███╗░░██╗░██████╗████████╗░█████╗░    ████████╗███████╗
        ██║████╗░██║██╔════╝╚══██╔══╝██╔══██╗    ╚══██╔══╝╚════██║
        ██║██╔██╗██║╚█████╗░░░░██║░░░███████║    ░░░██║░░░░░███╔═╝
        ██║██║╚████║░╚═══██╗░░░██║░░░██╔══██║    ░░░██║░░░██╔══╝░░
        ██║██║░╚███║██████╔╝░░░██║░░░██║░░██║    ░░░██║░░░███████╗
        ╚═╝╚═╝░░╚══╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝    ░░░╚═╝░░░╚══════╝
                    Instagram user OSINT/SOCMINT
                      github.com/georgehawkins0


Fetching posts: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 304/304 [00:20<00:00, 15.10it/s]
Hour   Frequency
0      ████████
1      █████████████
2      █████
3      ██████
4
5
6      ███
7
8      ██████
9      █
10     █████
11     ███
12     ████████
13     ████
14     ████
15     ██████
16     ████████████████
17     █████████████████████████████
18     ██████████████████████████████████████████
19     ████████████████████████████████
20     ██████████████████████████████████
21     ████████████████████████████
22     █████████████████████████
23     ██████████████████████████

 Estimated timezone: gmt -2


 Analysis of @github
 ```

 # About and Further reading

## Requirements

 The actual data collection makes use of [instagram_private_api](https://github.com/ping/instagram_private_api). [TQDM](https://github.com/tqdm/tqdm) is used for the progress bar and [Rich](https://github.com/Textualize/rich) is used for the pretty red colour of the banner.

## Further
This application generates a frequency per hour of post upload time of the target. Using this, it tries to work out the timezone of a user by taking into account the time the user will be inactive while asleep. However everyone has different lifestyles and as such this algorithm may be innacurate +/-3 hours, maybe more. However it is still a very useful insight into a users lifestyle.

Using this graph, you can also very quickly work out if the posts on the account are botted (if not obvious already) or posted by multiple people. A botted account will have no obvious rest period perhaps as such:
```Hour   Frequency
0      ████████
1      ██████████
2      █████████
3      █████████
4      ██████████
5      ██████████
6      █████████
7      ████████
8      █████████
9      ███████████
10     █████████
11     █████████
12     ██████████
13     █████████
14     ██████████
15     █████████
16     ████████
17     ██████████
18     █████████
19     ███████
20     ████████
21     ████████
22     █████████
23     ███████
```

However, an account which is not botted will look much more like this:

```
Hour   Frequency
0      ████████
1      █████████████
2      █████
3      ██████
4
5
6      █
7
8      ████
9      █
10     █████
11     ███
12     ████████
13     ████
14     ████
15     ██████
16     ████████████████
17     █████████████████████████████
18     ██████████████████████████████████████████
19     ████████████████████████████████
20     ██████████████████████████████████
21     ████████████████████████████
22     █████████████████████████
23     ██████████████████████████
```
Even glancing at this graph you can see obvious fluxuations in activity over time of day.

I have found this tool to be very informative if there is nothing other to analyse of a user. 
