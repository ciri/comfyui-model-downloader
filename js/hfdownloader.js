import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "HF Downloader",
    async setup() {        
        // Handle both node types
        const nodeTypes = ["HF Downloader", "CivitAI Downloader", "Auto Model Downloader"];
        
        nodeTypes.forEach(nodeType => {
            const origNode = LiteGraph.registered_node_types[nodeType];
            if (!origNode) {
                console.error(`Original node not found: ${nodeType}`);
                return;
            }

            // Override the title drawing
            origNode.prototype.onDrawTitleBar = function(ctx, titleHeight, size, scale, foregroundColor) {
                const titleWidth = Math.max(0, size[0]);

                ctx.save();
                ctx.fillStyle = this.color || foregroundColor;
                ctx.fillRect(0, -titleHeight, titleWidth, titleHeight);

                if (Number.isFinite(this.progress)) {
                    const progress = Math.min(1, Math.max(0, this.progress));
                    ctx.beginPath();
                    ctx.rect(0, -titleHeight, titleWidth, titleHeight);
                    ctx.clip();
                    ctx.fillStyle = "#2080ff66";
                    ctx.fillRect(0, -titleHeight, titleWidth * progress, titleHeight);
                }

                ctx.fillStyle = this.title_text_color || LiteGraph.NODE_TITLE_COLOR;
                ctx.font = `${LiteGraph.NODE_TEXT_SIZE}px Arial`;
                ctx.textAlign = "left";
                ctx.fillText(this.title, 4, -titleHeight * 0.3);
                ctx.restore();
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
            
            const value = Number(detail.value);
            const maximum = Number(detail.max);
            if (!Number.isFinite(value) || !Number.isFinite(maximum) || maximum <= 0) {
                return;
            }

            node.setProgress(Math.min(1, Math.max(0, value / maximum)));
        });
    }
});
