# this is an abstract base class for PR adapters
# it defines the interfaces that all the PR adapter must follow


from abc import ABC, abstractmethod
# from typing import TypedDict, Union
from typing import Union
from typing_extensions import TypedDict


class PRMeta(TypedDict):
    title: str
    author: str
    branch: str
    created_at: str
    description: str

class PullRequestClient(ABC):
    @abstractmethod
    def authenticate(self, token: str) -> None:
        """Authenticate with the version control system using an API token.
        
        Args:
            token: API token for authentication.
        """
        pass

    @abstractmethod
    def get_pr_meta(self, repo: str, pr_number: Union[str, int]) -> PRMeta:
        """Get PR metadata including title, author, branch, etc.
        
        Args:
            repo: Repository name (e.g., 'owner/repo').
            pr_number: Pull request number or ID.
        """
        pass

    @abstractmethod
    def get_pr_diff(self, repo: str, pr_number: Union[str, int]) -> str:
        """Return the unified diff of a PR as a string.
        
        Args:
            repo: Repository name (e.g., 'owner/repo').
            pr_number: Pull request number or ID.
        
        Returns:
            A string containing the unified diff.
        """
        pass

    def post_inline_comment(self, repo: str, pr_number: Union[str, int], file_path: str, line: int, body: str) -> None:
       
        raise NotImplementedError("Inline comments are not supported by this adapter.")
