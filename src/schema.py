import json


class Config(object):
    """
    An object to safely read, parse, load and provide configuration data
    """
    def __init__(self, filename: str) -> None:
        # Read config
        with open(filename, "r") as file:
            tmp: dict = json.load(file)

        # Parse and load config
        try:
            if not isinstance(tmp["api_key"], str):
                raise ValueError("'api_key' must be a string")
            if not isinstance(tmp["domains"], list):
                raise ValueError("'domains' must be an array")
            if not all(isinstance(x, str) for x in tmp["domains"]):
                raise ValueError("'domains' must be an array of strings")
            self.api_key = tmp["api_key"]
            self.domains = tmp["domains"]
        except KeyError:
            raise KeyError("Either 'api_key' or 'domains' is missing from config file")

        # No exceptions specified
        if not tmp.get("exceptions"):
            self.exceptions = None
        else:
            # Exceptions are defined
            self.exceptions = dict()
            try:
                for exception in tmp["exceptions"]:
                    if self.exception_valid_format(exception):
                        self.exceptions.update({exception["domain"]: exception["subdomains"]})
            except KeyError:
                raise KeyError("Exceptions are not correctly defined. "
                               "Consult template.json for recommended file format")
            # No exception met the required format
            if len(self.exceptions) == 0:
                self.exceptions = None

    @staticmethod
    def exception_valid_format(exception: dict[str, str | list[str]]) -> bool:
        """
        This method returns ``True`` if passed ``exception`` meets the following criteria:

        - The ``domain`` key has a value of type ``str``
        - The ``subdomains`` key has a value of type ``list``
        - The ``subdomains`` list has more than 0 items
        - All items of ``subdomains`` list are of type ``str``
        """
        if isinstance(exception["domain"], str):
            if isinstance(exception["subdomains"], list):
                if len(exception["subdomains"]) > 0:
                    if all(isinstance(x, str) for x in exception["subdomains"]):
                        return True
        return False

    api_key: str
    domains: list[str]
    exceptions: dict[str, list[str]] | None
