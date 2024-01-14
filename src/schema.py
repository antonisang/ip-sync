import json


class DomainExceptions(object):
    """
    An object that describes subdomains to be excepted from updating for a given domain
    """
    def __init__(self, domain: str, subdomains: list[str]) -> None:
        self.domain = domain
        self.subdomains = subdomains

    domain: str
    subdomains: list[str]


class Config(object):
    """
    An object to safely read, parse, load and provide configuration data
    """
    def __init__(self, filename: str) -> None:
        # Read config, in case of error, propagate error to be handled by main.py
        try:
            with open(filename, "r") as file:
                tmp: dict = json.load(file)
        except FileNotFoundError:
            raise FileNotFoundError("Couldn't locate config.json file")
        except ValueError:
            raise ValueError("Invalid config file")

        # Parse and load config
        self.api_key: str = tmp["api_key"]
        self.domains: list[str] = tmp["domains"]

        # No exceptions specified
        if not tmp.get("exceptions"):
            self.exceptions = None
        else:
            self.exceptions = list()
            for exception in tmp["exceptions"]:
                self.exceptions.append(DomainExceptions(exception["domain"], exception["subdomains"]))

    api_key: str
    domains: list[str]
    exceptions: list[DomainExceptions] | None
