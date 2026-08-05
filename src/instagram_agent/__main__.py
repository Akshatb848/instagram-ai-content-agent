import argparse


def main() -> None:
    parser = argparse.ArgumentParser(description="Instagram AI content agent utilities")
    parser.add_argument("command", choices=["health"], nargs="?", default="health")
    args = parser.parse_args()
    if args.command == "health":
        print("ok")


if __name__ == "__main__":
    main()
