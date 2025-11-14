import requests
import pandas as pd

url = "https://caching.graphql.imdb.com/?operationName=TitleReviewsRefine&variables=%7B%22after%22%3A%22g4xonermtizcs3yh7cuxvojvr3s4ycb23yntz4hqcwb32udfnyr2ucs4mjoln2sw64bzrhauwvqqoe5je6oci%22%2C%22const%22%3A%22tt0111161%22%2C%22filter%22%3A%7B%7D%2C%22first%22%3A25%2C%22locale%22%3A%22en-US%22%2C%22sort%22%3A%7B%22by%22%3A%22HELPFULNESS_SCORE%22%2C%22order%22%3A%22DESC%22%7D%7D&extensions=%7B%22persistedQuery%22%3A%7B%22sha256Hash%22%3A%22d389bc70c27f09c00b663705f0112254e8a7c75cde1cfd30e63a2d98c1080c87%22%2C%22version%22%3A1%7D%7D"

headers = {
    "accept": "application/graphql+json, application/json",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.imdb.com",
    "priority": "u=1, i",
    "referer": "https://www.imdb.com/",
    "sec-ch-ua": "\"Chromium\";v=\"142\", \"Google Chrome\";v=\"142\", \"Not_A Brand\";v=\"99\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "x-amzn-sessionid": "141-0344541-8691939",
    "x-imdb-client-name": "imdb-web-next-localized",
    "x-imdb-client-rid": "FCP7MDFB36YS1BY9W4G3",
    "x-imdb-consent-info": "eyJpc0dkcHIiOmZhbHNlfQ",
    "x-imdb-user-country": "US",
    "x-imdb-user-language": "en-US",
    "x-imdb-weblab-treatment-overrides": "{\"IMDB_NAV_PRO_FLY_OUT_1321244\":\"T1\",\"SEARCH_CONSUMER_CLUSTER_CLIENT_MIGRATION_1272244\":\"T1\"}",
    "Cookie": "session-id=141-0344541-8691939; session-id-time=2082787201l; ubid-main=134-8122907-7845338; ad-oo=0; ci=eyJpc0dkcHIiOmZhbHNlfQ; session-token=2imxvhi4FQOY/Nz0fE36RAGiiIlr/oXrH33sZrR44jl87XxCAQSTMFha+aDW2eN89U/6YuGqe0TWH33Y7xSmUpYjdxrxQ/laQ5HGKCTt4eJl29iUqCE6I21AFKaoxR8kuZjgKGbMA2fE1KsjH7kYTPxkUcSv108UzvnvIAKodDfyPRC7GH3NkYWqjdDmv38CjL+gO/Jv6efmIhKNmTVNuQxnSQT7u858PeOSYqLIbNCRzWZOFYgAjo7+IBLL2VsmJbiWQDSPp8mgXfn4193eW9Zqu0R6zb0MGNOh6QloTgIkMEzZQBJNEbcHUulAFfr3S/eTtS0y2VnGAPM71hvfiH6MpQUZTnv6."
}

response = requests.get(url, headers=headers, timeout=30)
# print(response.status_code)
# # print(response.text)
# print(response.json())


data = response.json()
print(data['data']['title']['reviews']['edges'])       

