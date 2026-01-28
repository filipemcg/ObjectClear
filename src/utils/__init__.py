import secrets
import string
import shutil

class FileUtils:
    @staticmethod
    def copy_file(source: str, destination: str) -> None:
        """Copy a file from source to destination."""
        shutil.copy(source, destination)

class Utils:
    @staticmethod
    def generate_identifier():
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(5))