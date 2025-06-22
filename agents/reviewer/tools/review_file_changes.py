import requests
from requests.auth import HTTPBasicAuth
import difflib

from langchain.chains import LLMChain
from langchain_core.tools import tool
from langchain.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from llms.openai import initialize_llm
from utils.parser import CustomJsonOutputParser
from utils.schemas import CodeSuggestionListSchema


def create_fetch_file(info: dict):

    @tool("fetch_file_changes")
    def fetch_file_changes() -> str:
        """
        This tool fetches file changes from the PR.

        :return: List of file changes
        """
        organization = info["organization"]
        project = info["project"]
        repository = info["repository"]
        pull_request_id = info["pull_request_id"]
        personal_access_token = info["personal_access_token"]
        full_code = info["full_code"]

        base_url = f"https://dev.azure.com/{organization}/{project}/_apis"
        repo_path = f"git/repositories/{repository}"
        auth = HTTPBasicAuth("", personal_access_token)
        headers = {"Content-Type": "application/json"}

        # ==== Step 1: Fetch base and target commits from PR ====
        pr_url = f"{base_url}/{repo_path}/pullRequests/{pull_request_id}?api-version=7.0"
        pr_response = requests.get(pr_url, auth=auth, headers=headers)
        pr_response.raise_for_status()
        pr_data = pr_response.json()

        base_commit = pr_data["lastMergeTargetCommit"]["commitId"]
        target_commit = pr_data["lastMergeSourceCommit"]["commitId"]

        # ==== Step 2: Fetch file-level diff ====
        diff_url = f"{base_url}/{repo_path}/diffs/commits?" \
                   f"baseVersion={base_commit}&baseVersionType=commit" \
                   f"&targetVersion={target_commit}&targetVersionType=commit&api-version=7.0"

        diff_response = requests.get(diff_url, auth=auth, headers=headers)
        diff_response.raise_for_status()
        diff_data = diff_response.json()

        results = []
        for change in diff_data.get("changes", []):
            item = change.get("item", {})
            if item.get("gitObjectType") != "blob":
                continue  # Skip folders or trees

            path = item["path"]
            change_type = change["changeType"]

            def fetch_lines(commit_sha):
                url = f"{base_url}/{repo_path}/items?path={path}&version={commit_sha}" \
                      f"&versionType=commit&includeContent=true&api-version=7.0"
                res = requests.get(url, auth=auth, headers=headers)
                if res.status_code == 200:
                    return res.text.splitlines()
                print(f"⚠️ Could not fetch content for {path} at {commit_sha}")
                return []

            before_lines = fetch_lines(base_commit)
            after_lines = fetch_lines(target_commit)

            file_content = ''
            if full_code:
                differ = difflib.Differ()
                diff = list(differ.compare(before_lines, after_lines))

                base_line_num = 1
                target_line_num = 1

                for line in diff:
                    content = line[2:]
                    if line.startswith('  '):
                        file_content += f"\n{base_line_num:4} │ {target_line_num:4} │   {content}"
                        base_line_num += 1
                        target_line_num += 1
                    elif line.startswith('- '):
                        file_content += f"\n{base_line_num:4} │ {'':4} │ - {content}"
                        base_line_num += 1
                    elif line.startswith('+ '):
                        file_content += f"\n{'':4} │ {target_line_num:4} │ + {content}"
                        target_line_num += 1
                    elif line.startswith('? '):
                        # Skip these diff hint lines
                        continue
                results.append({"file_path": path, "file_content": file_content})
            else:
                diff = list(difflib.unified_diff(before_lines, after_lines, lineterm="", n=3))

                base_line_no = 0
                new_line_no = 0

                for line in diff:
                    if line.startswith("@@"):
                        # Parse line numbers from chunk header
                        parts = line.split()
                        old_info = parts[1]
                        new_info = parts[2]
                        base_line_no = int(old_info.split(",")[0][1:])
                        new_line_no = int(new_info.split(",")[0][1:])
                        file_content += f"\n{line}"
                    elif line.startswith("-"):
                        file_content += f"\n{base_line_no:4} │ - {line[1:]}"
                        base_line_no += 1
                    elif line.startswith("+"):
                        file_content += f"\n{new_line_no:4} │ + {line[1:]}"
                        new_line_no += 1
                    else:
                        file_content += f"\n{new_line_no:4} │   {line[1:]}"
                        base_line_no += 1
                        new_line_no += 1

                results.append({"file_path": path, "file_content": file_content})
        return results

    return fetch_file_changes



@tool("review_file_changes")
def review_file_changes(file_path: str, file_content: str) -> str:
    """
    This tool will give suggestions on the basis of code changes in the file.

    Args:
       file_path (str): The path of the file.
       file_content (str): The content of the file with code changes

   :returns Suggestions for the code changes
   """
    parser = CustomJsonOutputParser(pydantic_object=CodeSuggestionListSchema)
    system_prompt = f"""
    You are a senior developer who reviews the code changes of a file and gives suggestions on code optimization and coding standards.

    {parser.get_schema_json()}
    """
    sys_prompt = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            input_variables=[],
            template=system_prompt
        )
    )
    human_prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="""
            FILE_PATH: 
            {file_path}

            FILE CONTENT:
            {file_content}
            """,
            input_variables=['file_path', 'file_content']
        )
    )
    chat_prompt = ChatPromptTemplate.from_messages([sys_prompt, human_prompt])

    llm = initialize_llm()

    chain = chat_prompt | llm | parser

    response = chain.invoke({"file_path": file_path, "file_content": file_content})

    return response