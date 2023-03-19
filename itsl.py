import argparse
from app import Application

import time
# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Command line interface for Itslearning.")
    parser.add_argument('--directory', type=str, help="Select the directory to put downloaded resources.")
    parser.add_argument('--no-ignore', help="When listing/downloading resources folders like Collaborate etc. should not be ignored.")
    args = parser.parse_args()

    app = Application(args)

    app.login_prompt()
    app.clear()

    # Logged in and ready to use itslearning

    app.list_courses()

    course = input("Select course: ")
    app.select_course(int(course))
    app.clear()

    # Course selected
    print(f"Selected course: {app.selected_course.title}")
    app.api.get_resources(app.selected_course)

    app.list_plans()

    for i in range(0, 101):
        print("hello")
        printProgressBar(i, 100, prefix = '', suffix = '', decimals = 1, length = 35, fill = '█', printEnd = "\r")
        time.sleep(0.1)

