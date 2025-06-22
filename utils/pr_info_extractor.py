from urllib.parse import urlparse, unquote
import re


def extract_azure_pr_info(url: str):
    parsed = urlparse(url)
    path_parts = parsed.path.strip("/").split("/")

    try:
        organization = path_parts[0]
        project = unquote(path_parts[1])
        repo_index = path_parts.index("_git") + 1
        repository = path_parts[repo_index]

        pr_id_match = re.search(r"pullrequest/(\d+)", url)
        pull_request_id = int(pr_id_match.group(1)) if pr_id_match else None

        if not pull_request_id:
            raise ValueError("Pull request ID not found in the URL")

        return {
            "organization": organization,
            "project": project,
            "repository": repository,
            "pull_request_id": pull_request_id
        }
    except Exception as e:
        print(f"Error parsing URL: {e}")
        return {}