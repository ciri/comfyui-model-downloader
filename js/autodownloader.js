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
    },
    async beforeRegisterNodeDef(nodeType, nodeData, app)  {
        if (nodeType.comfyClass == "Auto Model Downloader") {
            // Add missing_models to the properties that should be serialized
            const originalGetExtraProperties = nodeType.prototype.getExtraProperties;
            nodeType.prototype.getExtraProperties = function() {
                const props = originalGetExtraProperties ? originalGetExtraProperties.call(this) : [];
                props.push("missing_models");
                return props;
            };

            // Extend the node's prototype to add custom serialization
            const originalSerialize = nodeType.prototype.serialize;
            nodeType.prototype.serialize = function() {
                const data = originalSerialize ? originalSerialize.call(this) : {};
                if (this.missing_models) {
                    data.missing_models = this.missing_models;
                }
                return data;
            };

            // Store the original configure method
            const originalConfigure = nodeType.prototype.configure;

            // Restore method using configure
            nodeType.prototype.configure = function(data) {
                if (data.missing_models) {
                    this.missing_models = data.missing_models;
                }
                
                // Call original configure if it exists
                if (originalConfigure) {
                    originalConfigure.call(this, data);
                }

                // Update the widget after configuration
                if (this.missing_models) {
                    const selectWidget = this.widgets.find(w => w.name === "select_model");
                    if (selectWidget) {
                        const filenames = this.missing_models.map(m => m.filename);
                        selectWidget.options.values = filenames;
                        if (filenames.length > 0) {
                            selectWidget.value = filenames[0];
                        }
                        this.setDirtyCanvas(true);
                    }
                }
            };

            // Remove onConfigure as it's redundant with configure
            delete nodeType.prototype.onConfigure;
        }
    }
});