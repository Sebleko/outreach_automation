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
  public isRunning: boolean = false; // Expose for FlowExecutor checks
  private numWorkers: number;
  private priorityDecay: number;
  private reorderInterval: number;
  private reorderTimer: NodeJS.Timeout | null = null;

  constructor(
    numWorkers: number = 3,
    priorityDecay: number = 5,
    reorderInterval: number = 5000
  ) {
    this.numWorkers = numWorkers;
    this.priorityDecay = priorityDecay;
    this.reorderInterval = reorderInterval;
  }

  /** Adds a task to the queue */
  addTask(task: Task): void {
    this.taskQueue.push(task);
    this.resortQueue();
  }

  /** Start the scheduler with workers and periodic reordering */
  start(): void {
    if (this.isRunning) {
      console.log("[TaskScheduler] Already running.");
      return;
    }
    this.isRunning = true;

    // Start reorder timer
    this.reorderTimer = setInterval(
      () => this.reorderPriorities(),
      this.reorderInterval
    );

    // Start workers
    for (let i = 0; i < this.numWorkers; i++) {
      this.workers.push(this.worker());
    }
    console.log("[TaskScheduler] Scheduler started.");
  }

  /** Pause the scheduler: stops pulling NEW tasks but in-flight tasks continue. */
  async pause(): Promise<void> {
    if (!this.isRunning) {
      console.log("[TaskScheduler] Scheduler is not running, cannot pause.");
      return;
    }

    // Signal workers to stop after current tasks
    this.isRunning = false;

    // Stop reorder timer
    if (this.reorderTimer) {
      clearInterval(this.reorderTimer);
      this.reorderTimer = null;
    }

    // Wait for all current tasks to finish
    await Promise.all(this.workers);
    this.workers = [];

    console.log("[TaskScheduler] Scheduler paused.");
  }

  /** Gracefully shuts down the scheduler. (Alias of pause for clarity) */
  async shutdown(): Promise<void> {
    await this.pause();
    console.log("[TaskScheduler] Scheduler shut down.");
  }

  /** Worker that continuously processes tasks while isRunning is true */
  private async worker(): Promise<void> {
    while (this.isRunning) {
      const task = this.taskQueue.shift();
      if (!task) {
        // Queue is empty, slight delay to prevent busy-wait
        await new Promise((resolve) => setTimeout(resolve, 100));
        continue;
      }
      await task.process();
    }
  }

  /** Reorders tasks based on priority decay */
  private reorderPriorities(): void {
    if (!this.isRunning) return;

    const now = Date.now();
    for (let task of this.taskQueue) {
      const age = Math.floor((now - task.timestamp) / 1000);
      // The older the task, the more we reduce its numeric priority
      task.priority -= Math.floor(age / this.priorityDecay);
    }
    this.resortQueue();
  }

  private resortQueue() {
    // Sort ascending by priority (lower = higher priority)
    this.taskQueue.sort((a, b) => a.priority - b.priority);
  }
}
