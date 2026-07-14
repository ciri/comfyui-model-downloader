import re
import requests

_model_cache = {}

def search_for_model(filename):
    # Check cache first
    cache_key = filename.lower()
    if cache_key in _model_cache:
        return _model_cache[cache_key]

    def extract_model_components(filename):
        name_without_extension = re.sub(r'\.[^/.]+$', '', filename)
        parts = re.split(r'[-_]', name_without_extension)
        
        core_name = []
        version = None
        tags = []
        
        for part in parts:
            if re.match(r'v?\d+(-\d+)?', part):
                version = part
            elif re.match(r'[a-zA-Z]+', part):
                if not core_name:
                    core_name.append(part)
                else:
                    tags.append(part)
            elif core_name:
                tags.append(part)
        
        core_name = "_".join(core_name) if core_name else None
        return {"core_name": core_name, "version": version, "tags": tags}
    
    components = extract_model_components(filename)
    
    base_url = "https://huggingface.co/api/models"
    search_queries = []

    if components["core_name"]:
        if components["version"]:
            search_queries.append(f"{components['core_name']}_{components['version']}")
        if components["core_name"].lower() == "sd":
            alpha_tags = [tag for tag in components["tags"] if tag.isalpha()]
            if alpha_tags:
                search_queries.append(f"stable-diffusion-{alpha_tags[-1]}")
        search_queries.append(components["core_name"])
    combined_query = "_".join(
        part for part in [components["core_name"], *components["tags"]] if part
    )
    if combined_query:
        search_queries.append(combined_query)

    for query in dict.fromkeys(search_queries):
        response = requests.get(
            base_url,
            params={"full": "true", "search": query},
        )
        if response.status_code == 200:
            repos = response.json()
            if repos:
                for repo in repos:
                    match = next(
                        (
                            sibling
                            for sibling in repo.get("siblings", [])
                            if sibling["rfilename"] == filename
                        ),
                        None,
                    )
                    if match:
                        result = {"repo_id": repo["modelId"], "filename": filename}
                        _model_cache[cache_key] = result
                        return result
    _model_cache[cache_key] = None
    return None
