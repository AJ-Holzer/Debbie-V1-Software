import time

from env.classes.movement import Movement


def main() -> None:
    m = Movement()
    m.sit()

    time.sleep(4e6)


if __name__ == "__main__":
    main()
