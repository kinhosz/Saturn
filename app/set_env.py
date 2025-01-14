import argparse
from app.constant import set_env_name

def set_env():
    parser = argparse.ArgumentParser(description="Setting Environment")
    parser.add_argument('--environment', type=str, help="Environment Flag (ex: production, development, staging, test)", default='development')

    args = parser.parse_args()
    environment = args.environment

    if environment not in ['production', 'development', 'staging', 'test']:
        environment = 'development'

    set_env_name(environment)

    print("==============================")
    print(f"Environment '{environment}' set\n")
