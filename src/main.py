import argparse #модуль для обработки аргументов командной строки
import json #обрабатывает json
import urllib.request #отправка HTTP-запросов
import urllib.parse #разбор, создание и обработка URL-адресов
from collections import deque #структура данных очереди

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

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    return data["dependencies"]


# получение последней версии пакета
def get_latest_version(package, repository):
    parsed_url = urllib.parse.urlsplit(repository)

    api_url = (
        f"{parsed_url.scheme}://{parsed_url.netloc}"
        f"/api/v1/crates/{package}"
    )

    request = urllib.request.Request(
        api_url,
        headers={
            "User-Agent": "package-dependency-graph"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode("utf-8"))

    crate = data["crate"]

    return crate.get("max_stable_version") or crate["max_version"]


#функция получения зависимостей из тестового репозитория
def get_test_dependencies(repository):
    with open(repository, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data


#построение графа зависимостей с помощью BFS
def build_graph(dependencies, package, filter_substring, test_mode, version, repository):
    graph = {}
    queue = deque([package])
    visited = set()
    max_packages = 10

    while queue:
        current = queue.popleft()

        if current in visited:
            continue

        visited.add(current)
        print(f"Обрабатывается пакет: {current}")

        if len(visited) > max_packages:
            break

        if filter_substring in current:
            continue

        #получаем зависимости текущего пакета
        if test_mode:
            current_dependencies = dependencies.get(current, [])

        else:
            if current == package:
                current_version = version
            else:
                print(f"Получаем версию пакета {current}...")
                current_version = get_latest_version(current, repository)
                print(f"Получена версия: {current_version}")

            print(f"Получаем зависимости пакета {current}...")

            current_dependencies = get_dependencies(
                current, current_version, repository
            )

            print(f"Получено зависимостей: {len(current_dependencies)}")

            #оставляем только названия пакетов
            current_dependencies = [
                dependency["crate_id"]
                for dependency in current_dependencies
            ]

        graph[current] = []

        for dependency in current_dependencies:
            if filter_substring in dependency:
                continue

            graph[current].append(dependency)

            if dependency not in visited:
                queue.append(dependency)

    return graph

#поиск обратных зависимостей пакета
def find_reverse_dependencies(graph, package):
    reverse_dependencies = []

    for current_package, dependencies in graph.items():
        if package in dependencies:
            reverse_dependencies.append(current_package)

    return reverse_dependencies


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

    if args.test_mode:
        dependencies = get_test_dependencies(args.repository)
    else:
        dependencies = None

    graph = build_graph(
        dependencies,
        args.package,
        args.filter,
        args.test_mode,
        args.version,
        args.repository
    )

    print("Граф зависимостей:")
    print(graph)

    # поиск обратных зависимостей
    reverse_package = input("Введите название пакета для поиска обратных зависимостей: ")

    reverse_dependencies = find_reverse_dependencies(
        graph, reverse_package
    )

    print(f"Обратные зависимости пакета {reverse_package}:")

    if reverse_dependencies:
        for dependency in reverse_dependencies:
            print(dependency)
    else:
        print("Обратных зависимостей не найдено")

if __name__ == "__main__":
    main()