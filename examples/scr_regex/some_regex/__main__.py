import re


def find_email(text: str):
    pattern = r"[\w\.-]+@[\w\.-]+"
    return re.findall(pattern, text)


def run():
    text = "Hello, my email is example@email.com"
    matches = find_email(text)
    print(matches)


if __name__ == "__main__":
    run()
