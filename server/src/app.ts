import express from "express";
import cors from "cors";
import flowRouter from "./routes/flowRouter";
import businessRouter from "./routes/businessRouter";
import { config } from "dotenv";
import { AppDataSource } from "./data-source";
import { start as startFlowService } from "./services/flowService";

config(); // Load .env if necessary

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Register routes
app.use("/api/flows", flowRouter);
app.use("/api/businesses", businessRouter);

// Example global error handler
app.use((err, req, res, next) => {
  console.log("Global error handler", err);
  if (res.headersSent) {
    return next(err);
  }
  res.status(500);
  res.render("error", { error: err });
});

// Start server
const port = process.env.PORT || 4000;

AppDataSource.initialize()
  .then(() => {
    app.listen(port, () => {
      console.log(`Server running on port ${port}`);
    });
  })
  .then(startFlowService)
  .catch((err) => {
    console.error(err);
  });

export default app;
