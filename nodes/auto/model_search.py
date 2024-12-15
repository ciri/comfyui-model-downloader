import aiohttp
import re

async def search_for_model(filename):
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
    
    print(f"Searching for model: {filename}")
    components = extract_model_components(filename)
    print(f"Extracted components: {components}")

    base_url = "https://huggingface.co/api/models"
    search_queries = []

    if components["core_name"]:
        if components["version"]:
            search_queries.append(f"{components['core_name']}_{components['version']}")
        search_queries.append(components["core_name"])
    search_queries.append("_".join([components["core_name"], *components["tags"]]))

    async with aiohttp.ClientSession() as session:
        for query in search_queries:
            async with session.get(f"{base_url}?full=true&search={query}") as response:
                if response.status == 200:
                    repos = await response.json()
                    if repos:
                        for repo in repos:
                            match = next(
                                (sibling for sibling in repo.get("siblings", []) if sibling["rfilename"] == filename),
                                None
                            )
                            if match:
                                return {"repo_id": repo["modelId"], "filename": filename}
    return None
