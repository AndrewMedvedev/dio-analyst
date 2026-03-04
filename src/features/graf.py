import json
from collections import defaultdict, deque

from .links import data


def normalize_url(url: str) -> str:
    """Нормализация URL: убирает якоря, trailing slash и т.д."""
    if not url or not isinstance(url, str):
        return ""

    # Убираем якоря
    if "#" in url:
        url = url[: url.index("#")]

    # Убираем trailing slash для не-корневых URL
    known_roots = {"https://www.1ab.ru", "https://www.1ab.ru/"}
    if url not in known_roots and url.endswith("/"):
        url = url.rstrip("/")

    return url.strip()


def create_url_graph() -> tuple[dict[str, set[str]], set[str]]:
    """
    Создает граф связей между URL из JSON файла

    Args:
        json_file: путь к JSON файлу

    Returns:
        tuple: (граф связей, множество всех URL)

    Raises:
        FileNotFoundError: если файл не существует
        ValueError: если файл не является валидным JSON
    """
    # Проверка существования файла

    graph = defaultdict(set)
    urls = set()

    try:
        for item in data:
            # Проверка наличия обязательных полей
            if "url" not in item:
                print("Предупреждение: пропущен элемент без поля 'url'")
                continue

            source = normalize_url(item["url"])
            if not source:
                continue

            urls.add(source)

            # Обработка ссылок
            links = item.get("links", [])
            if not isinstance(links, list):
                print(f"Предупреждение: поле 'links' должно быть списком для URL {source}")
                continue

            for link in links:
                if not isinstance(link, str):
                    continue

                link = normalize_url(link)
                if link and link != source:  # Исключаем ссылки на самого себя
                    graph[source].add(link)
                    urls.add(link)

        if not urls:
            raise ValueError("В файле не найдено ни одного URL")

        return graph, urls

    except json.JSONDecodeError as e:
        raise ValueError(f"Некорректный JSON: {e}")


def find_root_url(urls: set[str]) -> str | None:
    """
    Находит корневую страницу сайта

    Args:
        urls: множество всех URL

    Returns:
        str: корневой URL или None, если не найден
    """
    # Известные корневые URL
    known_roots = ["https://www.1ab.ru", "https://www.1ab.ru/"]

    # Сначала проверяем известные корни
    for root in known_roots:
        if root in urls:
            return root

    # Если известных корней нет, ищем URL с минимальной глубиной пути
    def count_path_depth(url: str) -> int:
        """Считает количество сегментов пути после домена"""
        try:
            # Разбираем URL на части
            parts = url.split("/")
            # Отбрасываем протокол и домен (первые 3 части)
            path_parts = [p for p in parts[3:] if p]
            return len(path_parts)
        except:
            return float("inf")

    if urls:
        return min(urls, key=count_path_depth)

    return None


def find_similar_urls(urls: set[str], target_url: str, max_count: int = 3) -> list[str]:
    """
    Находит похожие URL (частичное совпадение)

    Args:
        urls: множество всех URL
        target_url: искомый URL
        max_count: максимальное количество предложений

    Returns:
        list: список похожих URL
    """
    similar = []
    target_lower = target_url.lower()

    for url in urls:
        url_lower = url.lower()
        # Проверяем вхождение в обе стороны
        if target_lower in url_lower or url_lower in target_lower:
            similar.append(url)
            if len(similar) >= max_count:
                break

    return similar


def find_path_to_url(target_url: str) -> tuple[int, list[str]]:
    """
    Находит минимальное количество переходов от главной страницы до target_url
    и сохраняет путь, по которому нужно пройти

    Args:
        json_file: путь к JSON файлу
        target_url: искомый URL

    Returns:
        tuple: (количество переходов, список URL пути)
               (-1, []) - URL не найден
               (-2, [похожие_url]) - точного совпадения нет, но есть похожие
               (-3, []) - ошибка файла
               (-4, []) - ошибка данных
               (-5, []) - непредвиденная ошибка
    """
    try:
        # Создаем граф
        graph, urls = create_url_graph()

        # Находим корневую страницу
        root = find_root_url(urls)
        if not root:
            print("Ошибка: не удалось определить корневую страницу")
            return (-1, [])

        # Нормализуем целевой URL
        target_url = normalize_url(target_url)

        # BFS с сохранением предков
        queue = deque([root])
        visited = {root}
        parent = {root: None}

        while queue:
            current = queue.popleft()

            if current == target_url:
                # Восстанавливаем путь
                path = []
                while current is not None:
                    path.append(current)
                    current = parent[current]
                path.reverse()
                return (len(path) - 1, path)

            # Проверяем всех соседей
            for neighbor in graph.get(current, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)

        # Если точное совпадение не найдено, ищем похожие
        similar_urls = find_similar_urls(urls, target_url)
        if similar_urls:
            return (-2, similar_urls)

        return (-1, [])

    except FileNotFoundError as e:
        print(f"Ошибка: {e}")
        return (-3, [])
    except ValueError as e:
        print(f"Ошибка в данных: {e}")
        return (-4, [])
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}")
        return (-5, [])


# Пример использования
if __name__ == "__main__":
    # Простой поиск
    result = find_path_to_url("https://www.1ab.ru/upload/medialibrary/351/budget_account_new.jpg")

    print(result)
