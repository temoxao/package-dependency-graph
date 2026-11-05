import argparse #модуль для обработки аргументов командной строки
import json #обрабатывает json
import urllib.request #отправка HTTP-запросов
import urllib.parse #разбор, создание и обработка URL-адресов

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


#функция получения зависимостей
def get_dependencies(package, version, repository):
    # Преобразуем адрес страницы crates.io в адрес API
    parsed_url = urllib.parse.urlsplit(repository)

    api_url = (
        f"{parsed_url.scheme}://{parsed_url.netloc}"
        f"/api/v1/crates/{package}/{version}/dependencies"
    )
    #создаем HTTP-запрос к серверу
    request = urllib.request.Request(
        api_url,
        headers={
            "User-Agent": "package-dependency-graph"
        }
    )

    with urllib.request.urlopen(request) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["dependencies"]

#вывод зависимостей
def print_dependencies(dependencies):
    print("Прямые зависимости:")

    for dependency in dependencies:
        print(
            f"{dependency['crate_id']} — "
            f"версия: {dependency['req']}, "
            f"тип: {dependency['kind']}, "
            f"необязательная: {dependency['optional']}"
        )


def main():
    args = parse_arguments()

    print(f"package: {args.package}")
    print(f"repository: {args.repository}")
    print(f"test_mode: {args.test_mode}")
    print(f"version: {args.version}")
    print(f"output: {args.output}")
    print(f"filter: {args.filter}")

    dependencies = get_dependencies(
            args.package,
            args.version,
            args.repository
    )

    print_dependencies(dependencies)

if __name__ == "__main__":
    main()