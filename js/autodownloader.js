import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

async function searchForModel(filename) {
    try {
        console.log("Searching for model:", filename);

        const baseUrl = "https://huggingface.co/api/models";
        const nameWithoutExtension = filename.replace(/\.[^/.]+$/, "");
        const parts = nameWithoutExtension.split(/[_]/);
    
        let searchQuery = nameWithoutExtension;
        let matchingResult = null;

        // Add authentication header if token exists
        const headers = {};
        //if (window.localStorage.getItem("hf_token")) {
        //    headers["Authorization"] = `Bearer ${window.localStorage.getItem("hf_token")}`;
        //}

        // Attempt progressively smaller queries
        for (let i = 1; i < parts.length; i++) {
            searchQuery = parts.slice(0, i).join("_");
            console.log(`Searching for: ${searchQuery}`);

            try {
                const response = await fetch(`${baseUrl}?full=True&search=${searchQuery}`, { headers });
                if (response.ok) {
                    const data = await response.json();
                    if (data.length > 0) {
                        console.log(`Results found for query: ${searchQuery}`);
                        for (const model of data) {
                            if (model.siblings) {
                                const match = model.siblings.find(
                                    (sibling) => sibling.rfilename === filename
                                );
                                if (match) {
                                    console.log(`Found exact match in repository: ${model.modelId}`);
                                    matchingResult = {
                                        repo_id: model.modelId,
                                        file: match,
                                    };
                                    break;
                                }
                            }
                        }
                    }
                } else {
                    console.log(`Search failed for ${searchQuery}: ${response.status}`);
                }
            } catch (error) {
                console.log(`Error searching for ${searchQuery}:`, error);
            }

            if (matchingResult) break;
        }

        if (matchingResult) {
            console.log(`Match found: ${matchingResult.repo_id}`);
            return {
                repo_id: matchingResult.repo_id,
                filename: filename
            };
        }
        console.error(`No exact match found for ${filename}`);
        return null;
    } catch (error) {
        console.error("Error in searchForModel:", error);
        return null;
    }
}

app.registerExtension({
    name: "Auto Model Downloader",
    async setup() {
        api.addEventListener("scan_complete", async ({ detail }) => {
            console.log("Scan complete event received:", detail);
            const node = app.graph.getNodeById(detail.node);
            if (!node || node.type !== "Auto Model Downloader") return;

            // Store models in node
            node.missing_models = detail.models.map(model => ({
                filename: model.filename,
                repo_id: model.repo_id
            }));

            // Search for each model
            for (const model of node.missing_models) {
                console.log(`Searching for: ${model.filename}`);
                const result = await searchForModel(model.filename);
                if (result) {
                    model.repo_id = result.repo_id;
                    console.log(`Found repo: ${result.repo_id} for ${model.filename}`);
                }
            }

            // Update Python node so it presents the options in the node widghet
            try {
                const response = await api.fetchApi('/customnode/comfyui-model-downloader/update_model_list', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: node.id,
                        method: "update_model_list",
                        models: node.missing_models
                    })
                });
                
                if (!response.ok) {
                    console.error("Failed to update model list:", response.status, response.statusText);
                    return;
                }
                
                // Update the widget in the UI
                const selectWidget = node.widgets.find(w => w.name === "select_model");
                if (selectWidget) {
                    const filenames = node.missing_models.map(m => m.filename);
                    selectWidget.options.values = filenames;
                    if (filenames.length > 0) {
                        selectWidget.value = filenames[0];
                        node.onWidgetChanged?.(selectWidget.name, selectWidget.value);
                    }
                    node.setDirtyCanvas(true);
                }
            } catch (error) {
                console.error("Error updating model list:", error);
            }
        });

        // Add handler for widget changes
        const origNode = LiteGraph.registered_node_types["Auto Model Downloader"];
        origNode.prototype.onWidgetChanged = function(name, value) {
            if (name === "select_model") {
                const selectedModel = this.missing_models?.find(m => m.filename === value);
                if (selectedModel) {
                    // Trigger a node update to refresh outputs
                    this.triggerSlot(0);
                    this.setDirtyCanvas(true);
                }
            }
        };
    }
});