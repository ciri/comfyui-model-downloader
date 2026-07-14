import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

function updateModelOptions(node, models) {
    node.missing_models = models;
    const selectWidget = node.widgets.find(w => w.name === "select_model");
    if (!selectWidget) return;

    const selections = node.missing_models.map(model => model.selection);
    selectWidget.options.values = selections;
    if (selections.length > 0 && !selections.includes(selectWidget.value)) {
        selectWidget.value = selections[0];
    }
    node.setDirtyCanvas(true);
}

app.registerExtension({
    name: "Auto Model Downloader",
    async setup() {
        api.addEventListener("scan_complete", async ({ detail }) => {
            console.log("Scan complete event received:", detail);
            const node = app.graph.getNodeById(detail.node);
            if (!node || node.type !== "Auto Model Downloader") return;

            try {                
                updateModelOptions(node, detail.models);
            } catch (error) {
                console.error("Error updating model list:", error);
            }
        });

    },
    async beforeRegisterNodeDef(nodeType, nodeData, app)  {
        if (nodeType.comfyClass == "Auto Model Downloader") {
            const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function() {
                originalOnNodeCreated?.call(this);
                this.addWidget("button", "rescan_models", "Rescan models", async () => {
                    try {
                        const { output } = await app.graphToPrompt();
                        const response = await api.fetchApi("/model-downloader/scan", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ prompt: output }),
                        });
                        if (!response.ok) throw new Error(await response.text());
                        const { models } = await response.json();
                        updateModelOptions(this, models);
                    } catch (error) {
                        console.error("Error rescanning models:", error);
                    }
                });
            };

            const synchronizeOutputLinks = (node) => {
                const graphLinks = node.graph?.links;
                if (!graphLinks) return;

                for (const output of node.outputs ?? []) {
                    output.links = [];
                }

                const links = graphLinks instanceof Map
                    ? graphLinks.values()
                    : Object.values(graphLinks);

                for (const link of links) {
                    const linkId = Array.isArray(link) ? link[0] : link.id;
                    const originId = Array.isArray(link) ? link[1] : link.origin_id;
                    const originSlot = Array.isArray(link) ? link[2] : link.origin_slot;
                    if (String(originId) !== String(node.id)) continue;

                    const output = node.outputs?.[originSlot];
                    if (output && !output.links.includes(linkId)) {
                        output.links.push(linkId);
                    }
                }

                node.setDirtyCanvas(true);
            };

            const originalConfigure = nodeType.prototype.configure;
            nodeType.prototype.configure = function(data) {
                if (originalConfigure) {
                    originalConfigure.call(this, data);
                }

                setTimeout(() => synchronizeOutputLinks(this), 0);
            };
        }
    }
});
