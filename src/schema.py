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
        # Read config
        with open(filename, "r") as file:
            tmp: dict = json.load(file)

        # Parse and load config
        try:
            self.api_key = tmp["api_key"]
            self.domains = tmp["domains"]
        except KeyError:
            raise KeyError("Either 'api_key' or 'domains' is missing from config file")

        # No exceptions specified
        if not tmp.get("exceptions"):
            self.exceptions = None
        else:
            self.exceptions = list()
            try:
                for exception in tmp["exceptions"]:
                    self.exceptions.append(DomainExceptions(exception["domain"], exception["subdomains"]))
            except KeyError:
                raise KeyError("Exceptions are not correctly defined. "
                               "Consult template.json for recommended file format")

    api_key: str
    domains: list[str]
    exceptions: list[DomainExceptions] | None
