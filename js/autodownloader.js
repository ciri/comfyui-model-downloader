import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "Auto Model Downloader",
    async setup() {
        api.addEventListener("scan_complete", async ({ detail }) => {
            console.log("Scan complete event received:", detail);
            const node = app.graph.getNodeById(detail.node);
            if (!node || node.type !== "Auto Model Downloader") return;

            try {                
                node.missing_models = detail.models;
                const selectWidget = node.widgets.find(w => w.name === "select_model");
                if (selectWidget) {
                    const selections = node.missing_models.map(model => model.selection);
                    selectWidget.options.values = selections;
                    if (selections.length > 0 && !selections.includes(selectWidget.value)) {
                        selectWidget.value = selections[0];
                    }
                    node.setDirtyCanvas(true);
                }
            } catch (error) {
                console.error("Error updating model list:", error);
            }
        });

    },
    async beforeRegisterNodeDef(nodeType, nodeData, app)  {
        if (nodeType.comfyClass == "Auto Model Downloader") {
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
