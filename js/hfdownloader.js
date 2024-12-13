import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

console.error("HFDownloader script loading");

app.registerExtension({
    name: "HF Downloader",
    async setup() {
        console.error("HF Downloader setup starting");

        const origNode = LiteGraph.registered_node_types["HF Downloader"];
        if (!origNode) {
            console.error("Original node not found");
            return;
        }

        // Override the title drawing
        origNode.prototype.onDrawTitleBar = function(ctx, title_height, size, collapsed) {
            if (this.progress !== undefined) {
                const progress = Math.min(100, Math.max(0, this.progress));
                const width = (size[0] * progress) / 100;
                
                ctx.save();
                ctx.fillStyle = "#2080ff44";
                const radius = 10;
                ctx.beginPath();
                ctx.roundRect(0, -title_height, width, title_height, [radius, radius, 0, 0]);
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
            console.error("Setting progress on node:", progress);
            this.progress = progress;
            this.setDirtyCanvas(true);
        };

        // Setup progress event listener
        api.addEventListener("progress", ({ detail }) => {
            console.error("Progress event received:", detail);
            if (!detail.node) return;
            
            const node = app.graph.getNodeById(detail.node);
            if (!node || node.type !== "HF Downloader") {
                console.error("Node not found or wrong type:", node?.type);
                return;
            }
            
            const progress = (detail.value / detail.max) * 100;
            console.error("Calling setProgress with:", progress);
            node.setProgress(progress);
        });

        console.error("HF Downloader setup complete");
    }
});