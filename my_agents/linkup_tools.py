import os
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from dotenv import load_dotenv

load_dotenv()


# Try to import the LangChain `tool` decorator. If LangChain is not
# installed, provide a no-op decorator so the module can still be imported
# and used without runtime errors.
try:
	from langchain.tools import tool
except Exception:  # pragma: no cover - optional dependency
	def tool(*_args, **_kwargs):
		def _decorator(func):
			return func

		return _decorator


class LinkupSearchRequest(BaseModel):
	query: str
	depth: Optional[str] = "standard"
	output_type: Optional[str] = "searchResults"
	include_images: Optional[bool] = False


class LinkupSearchResponse(BaseModel):
	success: bool
	status_code: Optional[int] = None
	raw: Dict[str, Any] = {}
	results: Optional[List[Any]] = None
	error: Optional[str] = None


def linkup_client():
	"""Create and return a LinkupClient.

	The function will use the provided `api_key` or fall back to the
	`LINKUP_API_KEY` environment variable. It will raise a helpful error
	if no key is available or if the `linkup` SDK is not installed.
	"""
	# Normalize to a single `api_key` variable sourced from the argument
	# or the environment. This keeps naming consistent across the module.
	
	api_key = os.getenv("LINKUP_API_KEY")
	
	try:
		# linkup-sdk 0.9.0 exports LinkupClient from linkup._client
		from linkup._client import LinkupClient  # type: ignore
	except ImportError:
		try:
			from linkup import LinkupClient  # type: ignore
		except Exception as e:  # pragma: no cover - dependency issue
			raise ImportError(
				"The `linkup` SDK is not available. Install it with `pip install linkup-sdk`"
			) from e

	return LinkupClient(api_key=api_key)


def linkup_search(request: LinkupSearchRequest) -> LinkupSearchResponse:
	"""Perform a Linkup search using the official SDK.

	Example usage:
		req = LinkupSearchRequest(query="What is Microsoft's revenue and operating income for 2024?", api_key=None)
		resp = linkup_search(req)

	By default the function will read the API key from the `LINKUP_API_KEY`
	environment variable unless `request.api_key` is provided.
	"""
	try:
		client = linkup_client()
	except Exception as e:
		return LinkupSearchResponse(success=False, error=str(e))

	try:
		# Build kwargs and call the SDK's search method
		kwargs: Dict[str, Any] = {
			"query": request.query,
			"depth": request.depth,
			"output_type": request.output_type,
			"include_images": request.include_images,
		}

		resp = client.search(**kwargs)

		# Normalize raw response into a dict where possible
		if isinstance(resp, dict):
			raw = resp
		else:
			# Try common attributes on SDK responses
			if hasattr(resp, "to_dict"):
				raw = resp.to_dict()
			elif hasattr(resp, "data"):
				raw = getattr(resp, "data") or {}
			else:
				# Fallback: try to coerce to dict
				try:
					raw = dict(resp)
				except Exception:
					raw = {"value": resp}

		results = raw.get("results") if isinstance(raw, dict) else None

		return LinkupSearchResponse(success=True, raw=raw, results=results)

	except Exception as e:
		return LinkupSearchResponse(success=False, error=str(e))





@tool("linkup_search")
def linkup_search_tool(
	query: str,
	depth: str = "standard",
) -> Dict[str, Any]:
	"""
    Searches the internet using the Linkup API.
    This tool allows you to perform web searches by providing a query string. 
    It returns a JSON-serializable dictionary containing the search results. 
    The search depth can be customized, and results do not include images.
    Args:
        query (str): The search query to look up on the internet.
        depth (str, optional): The depth of the search. Defaults to "standard". it can also take "deep".
    Returns:
        Dict[str, Any]: A dictionary containing the search results.
	"""
	req = LinkupSearchRequest(
		query=query,
		depth=depth,
		output_type="searchResults",
		include_images=False	
		)
	
	resp = linkup_search(req)
	# Return dict for tool compatibility
	return resp.model_dump()


if __name__ == "__main__":
    # Simple test
    query = "Find startups in the AI space founded after 2020 with Series A funding."
    
    resp = linkup_search_tool.invoke(input = {"query": query})
    print(resp)