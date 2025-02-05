export class Task {
  id: string;
  priority: number;
  timestamp: number;
  work: () => Promise<void>;

  constructor(id: string, priority: number, work: () => Promise<void>) {
    this.id = id;
    this.priority = priority;
    this.timestamp = Date.now();
    this.work = work;
  }

  async process(): Promise<void> {
    console.log(`Processing Task ${this.id} - Priority ${this.priority}`);
    await this.work();
    console.log(`Task ${this.id} completed!`);
  }
}

export class TaskScheduler {
  private taskQueue: Task[] = [];
  private workers: Promise<void>[] = [];
  private numWorkers: number;
  private priorityDecay: number;
  private reorderInterval: number;
  private isRunning: boolean = true;

  constructor(
    numWorkers: number = 3,
    priorityDecay: number = 5,
    reorderInterval: number = 5000
  ) {
    this.numWorkers = numWorkers;
    this.priorityDecay = priorityDecay; // How much priority increases over time
    this.reorderInterval = reorderInterval; // How often priorities are updated
  }

  /** Adds a task to the queue */
  addTask(task: Task): void {
    this.taskQueue.push(task);
    this.taskQueue.sort((a, b) => a.priority - b.priority); // Ensure min-heap order
  }

  /** Reorders tasks based on aging */
  private reorderPriorities(): void {
    setInterval(() => {
      if (!this.isRunning) return;

      const now = Date.now();
      for (let task of this.taskQueue) {
        const age = Math.floor((now - task.timestamp) / 1000);
        task.priority -= Math.floor(age / this.priorityDecay);
      }

      this.taskQueue.sort((a, b) => a.priority - b.priority); // Re-sort queue
      console.log("[Scheduler] Task priorities updated");
    }, this.reorderInterval);
  }

  /** Worker that continuously processes tasks */
  private async worker(): Promise<void> {
    while (this.isRunning) {
      const task = this.taskQueue.shift(); // Get highest priority task
      if (!task) {
        await new Promise((resolve) => setTimeout(resolve, 100)); // Avoid busy-waiting
        continue;
      }

      await task.process();
    }
  }

  /** Starts the scheduler with workers and periodic reordering */
  start(): void {
    this.reorderPriorities();
    for (let i = 0; i < this.numWorkers; i++) {
      this.workers.push(this.worker());
    }
  }

  /** Gracefully shuts down the scheduler */
  async shutdown(): Promise<void> {
    this.isRunning = false;
    await Promise.all(this.workers); // Wait for all workers to complete
    console.log("Scheduler stopped.");
  }
}
