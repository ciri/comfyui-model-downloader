import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

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

            // Update Python node so it presents the options in the node widget
            try {                
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