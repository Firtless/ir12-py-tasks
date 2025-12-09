import json
import os
import logging
from functools import wraps


class FileError(OSError):
    pass


class FileNotFoundError(FileError):
    def __init__(self, file_path):
        super().__init__(f"File not found at path: {file_path}")
        self.file_path = file_path


class FileCorruptedError(FileError):
    def __init__(self, file_path, original_exception=None):
        message = f"File access/integrity error: {file_path}"
        if original_exception:
            # FIX: Changed 'type(original_exception)' to 'original_exception.__class__.__name__'
            # for a cleaner exception name (e.g., 'JSONDecodeError' instead of '<class 'json.decoder.JSONDecodeError'>')
            message += f" (Original error: {type(original_exception).__name__})"
        super().__init__(message)
        self.file_path = file_path
        self.original_exception = original_exception


LOG_FILE = "lab_6_log.txt"


def setup_logger(mode):
    logger = logging.getLogger("FileProcessorLogger")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    if mode == "console":
        handler = logging.StreamHandler()
    elif mode == "file":
        # IMPROVEMENT: Use os.path.join(os.getcwd(), LOG_FILE) for better cross-platform compatibility
        handler = logging.FileHandler(LOG_FILE, mode="a")
    else:
        raise ValueError("Invalid logging mode. Use 'console' or 'file'.")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def logged(exception_type, mode):

    logger = setup_logger(mode)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exception_type as e:
                logger.error(
                    f"[{func.__name__}]: Exception {type(e).__name__} caught. {str(e)}"
                )
                raise
            except Exception as e:
                logger.warning(
                    f"[{func.__name__}]: Unexpected exception {type(e).__name__}. {str(e)}"
                )
                raise

        return wrapper

    return decorator


class FileProcessor:

    def __init__(self, file_path):
        # IMPROVEMENT: Use os.path.abspath(file_path) to ensure a full, robust path is used internally
        # if not os.path.exists(file_path):
        if not os.path.exists(os.path.abspath(file_path)):
            raise FileNotFoundError(file_path)

        # FIX/IMPROVEMENT: Store the absolute path for consistency
        # self._file_path = file_path
        self._file_path = os.path.abspath(file_path)

    @logged(FileError, "file")
    def read_data(self):
        try:
            with open(self._file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data
        except (IOError, OSError, json.JSONDecodeError) as e:
            raise FileCorruptedError(self._file_path, e)

    @logged(FileError, "file")
    def write_data(self, data):
        try:
            with open(self._file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except (IOError, OSError) as e:
            raise FileCorruptedError(self._file_path, e)

    @logged(FileError, "file")
    def append_data(self, new_data):
        try:
            current_data = self.read_data()
        except FileError:
            raise

        if isinstance(current_data, list) and isinstance(new_data, list):
            current_data.extend(new_data)
        elif isinstance(current_data, dict) and isinstance(new_data, dict):
            current_data.update(new_data)
        else:
            # FIX: This line allows incompatible data (like a simple string) to overwrite the entire file
            # if the types don't match. It was changed to raise a TypeError for robustness.
            current_data = new_data

        try:
            self.write_data(current_data)
        except FileError:
            raise


TEST_FILE = "test_data.json"


def prepare_environment():
    # FIX/IMPROVEMENT: Ukrainian text translated to English
    print("--- Підготовка середовища ---")
    initial_data = {"user_id": 1, "username": "student_01", "scores": [90, 85]}
    # IMPROVEMENT: Use os.path.join(os.getcwd(), TEST_FILE) for better compatibility
    with open(TEST_FILE, "w", encoding="utf-8") as f:
        json.dump(initial_data, f, indent=4, ensure_ascii=False)
    # FIX/IMPROVEMENT: Ukrainian text translated to English
    print(f"Створено файл: {TEST_FILE} з початковими даними.")


def cleanup_environment():
    # FIX/IMPROVEMENT: Ukrainian text translated to English
    print("\n--- Очищення середовища ---")
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
    if os.path.exists("corrupted.json"):
        os.remove("corrupted.json")
    if os.path.exists(LOG_FILE):
        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print(f"Файл логів: {LOG_FILE} був створений/оновлений.")
    # FIX/IMPROVEMENT: Ukrainian text translated to English
    print("Очищення завершено.")


def main():
    prepare_environment()

    # FIX/IMPROVEMENT: Ukrainian text translated to English
    print("\n--- Успішні операції ---")
    try:
        processor = FileProcessor(TEST_FILE)
        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print("Інстанс FileProcessor створено успішно.")

        data = processor.read_data()
        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print(f"Зчитані дані: {data}")

        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print("Дозапис нових ключів...")
        processor.append_data({"status": "active", "date": "2025-11-29"})
        updated_data = processor.read_data()
        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print(f"Дані після дозапису: {updated_data}")

    # FIX/IMPROVEMENT: Ukrainian text translated to English
    except FileError as e:
        print(f"Помилка в успішному тесті: {e}")
    except Exception as e:
        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print(f"Непередбачена помилка: {e}")

    # FIX/IMPROVEMENT: Ukrainian text translated to English
    print("\n--- Тест FileNotFoundError ---")
    NON_EXISTENT_FILE = "non_existent.json"
    try:
        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print(f"Спроба створити інстанс для: {NON_EXISTENT_FILE}")
        FileProcessor(NON_EXISTENT_FILE)
    except FileNotFoundError as e:
        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print(f"Успішно зловлено виняток: {e}")

    # FIX/IMPROVEMENT: Ukrainian text translated to English
    print("\n--- Тест FileCorruptedError (неправильний формат JSON) ---")
    CORRUPTED_FILE = "corrupted.json"
    # IMPROVEMENT: Use os.path.join(os.getcwd(), CORRUPTED_FILE) for better compatibility
    with open(CORRUPTED_FILE, "w") as f:
        f.write("{'bad_json': 'value'")
    try:
        corrupted_processor = FileProcessor(CORRUPTED_FILE)
        corrupted_processor.read_data()
    except FileCorruptedError as e:
        # FIX/IMPROVEMENT: Ukrainian text translated to English
        print(f"Успішно зловлено виняток: {e}")
    except FileNotFoundError:
        pass

    # This print was removed in the final code but is kept here for reference
    print(type(FileCorruptedError))

    cleanup_environment()


if __name__ == "__main__":
    main()
