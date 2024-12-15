import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "HF Downloader",
    async setup() {        
        // Handle both node types
        const nodeTypes = ["HF Downloader", "Auto Model Downloader"];
        
        nodeTypes.forEach(nodeType => {
            const origNode = LiteGraph.registered_node_types[nodeType];
            if (!origNode) {
                console.error(`Original node not found: ${nodeType}`);
                return;
            }

            // Override the title drawing
            origNode.prototype.onDrawTitleBar = function(ctx, title_height, size, collapsed) {
                if (this.progress !== undefined) {
                    const progress = Math.min(100, Math.max(0, this.progress));
                    const width = (size[0] * progress) / 100;
                    
                    ctx.save();
                    ctx.fillStyle = "#2080ff44";
                    const radius = 4;
                    ctx.beginPath();
                    ctx.roundRect(0, 0, width, title_height, [radius, radius, 0, 0]);
                    ctx.fill();
                    ctx.restore();
                }

                if (!collapsed) {
                    ctx.fillStyle = "#fff";
                    ctx.font = LiteGraph.NODE_TEXT_SIZE + "px Arial";
                    ctx.textAlign = "left";
                    ctx.fillText(this.title, 4, title_height * 0.7);
                }
            };

            // Add progress handling method
            origNode.prototype.setProgress = function(progress) {
                this.progress = progress
                this.setDirtyCanvas(true);
            };
        });

        // Setup progress event listener for both node types
        api.addEventListener("progress", ({ detail }) => {
            if (!detail.node) return;
            
            const node = app.graph.getNodeById(detail.node);
            if (!node || !nodeTypes.includes(node.type)) {
                console.error("Node not found or wrong type:", node?.type);
                return;
            }
            
            const progress = (detail.value / detail.max) * 100;
            node.setProgress(progress);
        });
    }
});