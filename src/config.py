import os


def get_db_url():
    if os.getenv("PROD"):
        return os.getenv("DB_URL")
    if os.getenv("STAGING"):
        return os.getenv("DB_URL_INT_STABLE")
    return os.getenv("DB_URL_DEV")


def get_app_url() -> str:
    # waterfall assignment in order of priority
    if os.getenv("PROD"):
        return "https://cyoa-app-prod.herokuapp.com"
    if os.getenv("STAGING"):
        return "https://cyoa-app-int-stable.herokuapp.com"
    return "http://localhost:3000"
