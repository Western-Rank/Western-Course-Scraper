import requests

url = "https://www.ratemyprofessors.com/graphql"
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9,ta-IN;q=0.8,ta;q=0.7",
    "authorization": "Basic dGVzdDp0ZXN0",
    "content-type": "application/json",
    "sec-ch-ua": "\"Not.A/Brand\";v=\"8\", \"Chromium\";v=\"114\", \"Google Chrome\";v=\"114\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin"
}
referrer = "https://www.ratemyprofessors.com/search/professors/1491?q=*"
referrer_policy = "strict-origin-when-cross-origin"
body = {
    "query": "query TeacherSearchPaginationQuery(\n  $count: Int!\n  $cursor: String\n  $query: TeacherSearchQuery!\n) {\n  search: newSearch {\n    ...TeacherSearchPagination_search_1jWD3d\n  }\n}\n\nfragment TeacherSearchPagination_search_1jWD3d on newSearch {\n  teachers(query: $query, first: $count, after: $cursor) {\n    didFallback\n    edges {\n      cursor\n      node {\n        ...TeacherCard_teacher\n        id\n        __typename\n      }\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n    resultCount\n    filters {\n      field\n      options {\n        value\n        id\n      }\n    }\n  }\n}\n\nfragment TeacherCard_teacher on Teacher {\n  id\n  legacyId\n  avgRating\n  numRatings\n  ...CardFeedback_teacher\n  ...CardSchool_teacher\n  ...CardName_teacher\n  ...TeacherBookmark_teacher\n}\n\nfragment CardFeedback_teacher on Teacher {\n  wouldTakeAgainPercent\n  avgDifficulty\n}\n\nfragment CardSchool_teacher on Teacher {\n  department\n  school {\n    name\n    id\n  }\n}\n\nfragment CardName_teacher on Teacher {\n  firstName\n  lastName\n}\n\nfragment TeacherBookmark_teacher on Teacher {\n  id\n  isSaved\n}\n",
    "variables": {
        "count": 3000,
        "cursor": "YXJyYXljb25uZWN0aW9uOjc=",
        "query": {
            "text": "",
            "schoolID": "U2Nob29sLTE0OTE=",
            "fallback": True,
            "departmentID": None
        }
    }
}
method = "POST"
mode = "cors"
credentials = "include"

response = requests.post(url, headers=headers, json=body)
with open("profs.json", "wb") as output:
    output.write(response.content)


