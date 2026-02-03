try:
    from duckduckgo_search import DDGS
    print("SUCCESS: imported DDGS from duckduckgo_search")
except ImportError:
    print("FAILURE: could not import DDGS from duckduckgo_search")

try:
    import ddgs
    print("SUCCESS: imported ddgs")
except ImportError:
    print("FAILURE: could not import ddgs")
