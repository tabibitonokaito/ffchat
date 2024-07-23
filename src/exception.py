

class NotExactMatch(Exception):
    def __init__(self, message: str, results=None):
        super().__init__(message)
        self.results = results


class MultipleFoundError(NotExactMatch):
    def __init__(self, results):
        super().__init__(f"Multiple targets found. Results: {results}", results)


class NotFoundError(NotExactMatch):
    def __init__(self):
        super().__init__("Target not found.", None)  # No results to include


