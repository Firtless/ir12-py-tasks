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
            message += f" (Original error: {original_exception.__class__.__name__})"
        super().__init__(message)
        self.file_path = file_path
        self.original_exception = original_exception


LOG_FILE_NAME = "lab_6_log.txt"


def setup_logger(mode):
    logger = logging.getLogger("FileProcessorLogger")
    logger.setLevel(logging.INFO)

    if logger.hasHandlers():
        logger.handlers.clear()

    if mode == "console":
        handler = logging.StreamHandler()
    elif mode == "file":
        log_path = os.path.join(os.getcwd(), LOG_FILE_NAME)
        handler = logging.FileHandler(log_path, mode="a")
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
        self._file_path = os.path.abspath(file_path)
        if not os.path.exists(self._file_path):
            raise FileNotFoundError(self._file_path)

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
            error_msg = (
                f"Cannot append data of type '{type(new_data).__name__}' "
                f"to existing data of type '{type(current_data).__name__}'."
            )
            raise TypeError(error_msg)

        try:
            self.write_data(current_data)
        except FileError:
            raise


TEST_FILE_NAME = "test_data.json"


def prepare_environment():
    print("--- Environment Setup ---")

    test_path = os.path.join(os.getcwd(), TEST_FILE_NAME)

    initial_data = {"user_id": 1, "username": "student_01", "scores": [90, 85]}
    with open(test_path, "w", encoding="utf-8") as f:
        json.dump(initial_data, f, indent=4, ensure_ascii=False)
    print(f"File created: {TEST_FILE_NAME} with initial data.")
    return test_path


def cleanup_environment():
    print("\n--- Environment Cleanup ---")

    test_path = os.path.join(os.getcwd(), TEST_FILE_NAME)
    corrupted_path = os.path.join(os.getcwd(), "corrupted.json")
    log_path = os.path.join(os.getcwd(), LOG_FILE_NAME)

    if os.path.exists(test_path):
        os.remove(test_path)
    if os.path.exists(corrupted_path):
        os.remove(corrupted_path)

    if os.path.exists(log_path):
        print(f"Log file: {LOG_FILE_NAME} was created/updated.")
    print("Cleanup complete.")


def main():
    test_file_path = prepare_environment()

    print("\n--- Successful Operations ---")
    try:
        processor = FileProcessor(test_file_path)
        print("FileProcessor instance created successfully.")

        data = processor.read_data()
        print(f"Data read: {data}")

        print("Appending new keys...")
        processor.append_data({"status": "active", "date": "2025-11-29"})
        updated_data = processor.read_data()
        print(f"Data after appending: {updated_data}")

    except FileError as e:
        print(f"Error in successful test: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    print("\n--- Test FileNotFoundError ---")
    NON_EXISTENT_FILE = os.path.join(os.getcwd(), "non_existent.json")
    try:
        print(
            f"Attempting to create instance for: {os.path.basename(NON_EXISTENT_FILE)}")
        FileProcessor(NON_EXISTENT_FILE)
    except FileNotFoundError as e:
        print(f"Exception successfully caught: {e}")

    print("\n--- Test FileCorruptedError (Invalid JSON format) ---")
    CORRUPTED_FILE = os.path.join(os.getcwd(), "corrupted.json")
    with open(CORRUPTED_FILE, "w") as f:
        f.write("{'bad_json': 'value'")
    try:
        corrupted_processor = FileProcessor(CORRUPTED_FILE)
        corrupted_processor.read_data()
    except FileCorruptedError as e:
        print(f"Exception successfully caught: {e}")
    except FileNotFoundError:
        pass

    print("\n--- Test Type Error (Incompatible Append) ---")
    try:
        processor = FileProcessor(test_file_path)
        print("Attempting to append incompatible data (str to dict)...")
        processor.append_data("This should fail")
    except TypeError as e:
        print(f"Exception successfully caught: {e}")
    except FileError as e:
        print(f"FileError: {e}")

    cleanup_environment()


if __name__ == "__main__":
    main()
