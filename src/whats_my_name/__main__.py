from .web_accounts_list_checker import WebAccountsListChecker


def main():
    """
    Function to kick off the show.
    """
    checker = WebAccountsListChecker()
    checker.run()
    print "Finished"


if __name__ == "__main__":
    main()
