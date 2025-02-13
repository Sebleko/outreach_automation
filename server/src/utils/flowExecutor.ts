import { AppDataSource } from "../data-source";
import { BusinessPathEntity } from "../entity/BusinessPath";
import { Flow } from "../entity/Flow";
import { PathStatus } from "../../../shared/models";
import { Task, TaskScheduler } from "./taskScheduling";

export class FlowExecutor {
  private flowId: number | null = null;
  private paths: BusinessPathEntity[] = [];
  private scheduler: TaskScheduler;
  private isPaused: boolean = false;
  private isLoaded: boolean = false;

  constructor(scheduler?: TaskScheduler) {
    // Allows injecting a scheduler or creating a new default one
    this.scheduler =
      scheduler ||
      new TaskScheduler(
        3, // numWorkers
        5, // priorityDecay
        5000 // reorderInterval in ms
      );
  }

  /**
   * Loads the Flow from DB and initializes internal state.
   */
  public async load(flowId: number): Promise<void> {
    this.flowId = flowId;

    const flowRepo = AppDataSource.getRepository(Flow);
    const flow = await flowRepo.findOneBy({ id: flowId });
    if (!flow) {
      throw new Error(`Flow with ID ${flowId} not found.`);
    }

    const mappingRepo = AppDataSource.getRepository(BusinessPathEntity);
    this.paths = await mappingRepo.find({
      where: { flow: { id: flowId } },
      relations: ["business"],
    });

    // Ensure all paths have a status set
    for (const path of this.paths) {
      if (!path.status) {
        console.warn("Path", path.id, "missing status; setting to Pending");
        path.status = PathStatus.Pending;
      }
    }

    this.isLoaded = true;
    console.log(
      `[FlowExecutor] Loaded flow ${flowId} with ${this.paths.length} paths`
    );
  }

  /**
   * Start the scheduler and enqueue tasks for all relevant paths.
   * If paused, resumes the scheduler.
   */
  public start(): void {
    if (!this.isLoaded) {
      throw new Error("FlowExecutor not loaded. Call load(flowId) first.");
    }

    if (this.isPaused) {
      // Resuming
      this.isPaused = false;
      this.scheduler.start();
      console.log("[FlowExecutor] Resumed execution");
      return;
    }

    // If the scheduler is already running, do nothing
    if (this.scheduler.isRunning) {
      console.log("[FlowExecutor] Scheduler is already running.");
      return;
    }

    // Enqueue tasks for each path not in a terminal state
    for (const path of this.paths) {
      if (
        path.status !== PathStatus.Done &&
        path.status !== PathStatus.Failed
      ) {
        const task = new Task(
          String(path.id),
          this.computePriority(path),
          async () => {
            await this.processPath(path);
          }
        );
        this.scheduler.addTask(task);
      }
    }

    // Start worker threads
    this.scheduler.start();
    console.log("[FlowExecutor] Started execution");
  }

  /**
   * Pause the scheduler: no new tasks will be processed,
   * but in-flight tasks complete.
   */
  public async pause(): Promise<void> {
    if (!this.scheduler.isRunning) {
      console.log("[FlowExecutor] No active scheduler to pause.");
      return;
    }

    this.isPaused = true;
    await this.scheduler.pause();
    console.log("[FlowExecutor] Paused execution.");
  }

  /**
   * Approve either the report or the outreach for a specific path.
   * This transitions the path from its "Awaiting" state to its "Approved" state,
   * then enqueues a new task to continue processing.
   */
  public async approve(
    pathId: string,
    approvalType: "report" | "outreach"
  ): Promise<void> {
    if (!this.isLoaded) {
      throw new Error("FlowExecutor not loaded. Call load(flowId) first.");
    }

    // Find the path in memory (faster) or load from DB
    let path = this.paths.find((p) => String(p.id) === pathId);
    if (!path) {
      throw new Error(`Path with ID ${pathId} not found.`);
    }

    // Check the current status and update accordingly
    if (approvalType === "report") {
      if (path.status !== PathStatus.AwaitingReportApproval) {
        throw new Error(`Path ${pathId} is not awaiting report approval.`);
      }
      path.status = PathStatus.ReportApproved;
    } else {
      if (path.status !== PathStatus.AwaitingOutreachApproval) {
        throw new Error(`Path ${pathId} is not awaiting outreach approval.`);
      }
      path.status = PathStatus.OutreachApproved;
    }

    // Persist status update
    await AppDataSource.getRepository(BusinessPathEntity).save(path);
    console.log(
      `[FlowExecutor] Path ${pathId} ${approvalType} approved. Status: ${path.status}`
    );

    // Enqueue a new task to continue processing from this new status
    const nextTask = new Task(
      String(path.id),
      this.computePriority(path),
      async () => {
        await this.processPath(path);
      }
    );
    this.scheduler.addTask(nextTask);

    // If we're not paused, ensure the scheduler is running (it might already be)
    if (!this.isPaused && !this.scheduler.isRunning) {
      this.scheduler.start();
    }
  }

  /**
   * Core logic to handle a single path's workflow stage transitions.
   */
  private async processPath(path: BusinessPathEntity): Promise<void> {
    switch (path.status) {
      case PathStatus.Pending: {
        // Move to "ExplorationInProgress"
        path.status = PathStatus.ExplorationInProgress;
        await this.savePath(path);
        await this.fakeAsyncDelay(3000 + 100000 * Math.random());

        // Then automatically assume we have a "report" that needs approval
        path.status = PathStatus.AwaitingReportApproval;
        await this.savePath(path);
        break;
      }

      case PathStatus.ReportApproved: {
        // Move to "OutreachGenerationInProgress"
        path.status = PathStatus.OutreachGenerationInProgress;
        await this.savePath(path);
        await this.fakeAsyncDelay(3000 + Math.random() * 2000);

        // Then we require outreach approval
        path.status = PathStatus.AwaitingOutreachApproval;
        await this.savePath(path);
        break;
      }

      case PathStatus.OutreachApproved: {
        // “Send” the outreach
        path.status = PathStatus.Sent;
        await this.savePath(path);
        await this.fakeAsyncDelay(500);

        // Mark as done
        path.status = PathStatus.Done;
        await this.savePath(path);
        break;
      }

      // For these states, there's no automatic progression:
      // They either require manual approval or are terminal
      case PathStatus.ExplorationInProgress:
      case PathStatus.AwaitingReportApproval:
      case PathStatus.AwaitingOutreachApproval:
      case PathStatus.Paused:
      case PathStatus.Failed:
      case PathStatus.Done:
      case PathStatus.Sent:
      default:
        // No changes; we end the task here
        break;
    }
  }

  /**
   * Compute a priority from the path’s status or other attributes.
   * Lower number = higher priority in the default scheduler.
   */
  private computePriority(path: BusinessPathEntity): number {
    switch (path.status) {
      case PathStatus.Pending:
        return 1;
      case PathStatus.ReportApproved:
      case PathStatus.OutreachApproved:
        return 2;
      default:
        return 5;
    }
  }

  /**
   * Persists the path to the DB.
   */
  private async savePath(path: BusinessPathEntity): Promise<void> {
    await AppDataSource.getRepository(BusinessPathEntity).save(path);
  }

  /**
   * Simulates an asynchronous step.
   */
  private async fakeAsyncDelay(ms: number) {
    return new Promise<void>((resolve) => setTimeout(resolve, ms));
  }
}
