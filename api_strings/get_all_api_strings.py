from APIStringGenerator import *
import json
import requests

if __name__ == '__main__':
    with open("locals.csv", "r") as read_file:
        locals = read_file.read().split(",")
        for locale in locals:
            url_str = APIStringGenerator.get_API_string_for_string_list(locale)
            response = requests.get(url_str)
            strings = json.loads(response.text)
            with open("strings_{}.json".format(locale), "w") as write_file:
                json.dump(strings, write_file, indent=2)

