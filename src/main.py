#модуль для обработки аргументов командной строки
import argparse

#проверка что поле не пустое и не состоит из пробелов
def check_not_empty(value):
    #если строка после удаления пробелов путсая
    if not value.strip():
        print("Ошибка: значение не должно быть пустым")
        exit(1)

    return value

#проверяет что поле test принимает только true и false
def check_test_mode(value):
    if value != "true" and value != "false":
        print("Ошибка: режим должен быть true или false")
        exit(1)

    return value == "true"

#парсер строки на аргументы
def parse_arguments():
    parser = argparse.ArgumentParser()
    # регистрация аргументов
    parser.add_argument("--package", required=True, type=check_not_empty)
    parser.add_argument("--repository", required=True, type=check_not_empty)
    parser.add_argument("--test-mode", required=True, type=check_test_mode)
    parser.add_argument("--version", required=True, type=check_not_empty)
    parser.add_argument("--output", required=True, type=check_not_empty)
    parser.add_argument("--filter", required=True, type=check_not_empty)

    return parser.parse_args()


def main():
    args = parse_arguments()

    print(f"package: {args.package}")
    print(f"repository: {args.repository}")
    print(f"test_mode: {args.test_mode}")
    print(f"version: {args.version}")
    print(f"output: {args.output}")
    print(f"filter: {args.filter}")


if __name__ == "__main__":
    main()
