import { spawn, ChildProcess } from "child_process";
import { join } from "path";

const REQUEST_TIMEOUT_MS = 30_000;

interface RpcRequest {
  id: number;
  method: string;
  params: Record<string, unknown>;
}

interface RpcResponse {
  id: number | null;
  result?: unknown;
  error?: string;
}

type PendingRequest = {
  resolve: (value: unknown) => void;
  reject: (reason: Error) => void;
  timer: NodeJS.Timeout;
};

export class PythonBridge {
  private process: ChildProcess | null = null;
  private pending = new Map<number, PendingRequest>();
  private nextId = 1;
  private buffer = Buffer.alloc(0);
  private enginePath: string;

  constructor(enginePath?: string) {
    this.enginePath = enginePath ?? join(__dirname, "..", "..", "..", "embedding-engine", "src", "main.py");
  }

  start(): void {
    if (this.process) return;

    const pythonBin = process.platform === "win32" ? "python" : "python3";
    this.process = spawn(pythonBin, [this.enginePath], {
      stdio: ["pipe", "pipe", "pipe"],
    });

    this.process.stdout!.on("data", (chunk: Buffer) => {
      this.buffer = Buffer.concat([this.buffer, chunk]);
      this.drainBuffer();
    });

    this.process.stderr!.on("data", (data: Buffer) => {
      const msg = data.toString().trim();
      if (msg) process.stderr.write(`[python-engine] ${msg}\n`);
    });

    this.process.on("exit", (code) => {
      process.stderr.write(`[python-engine] exited with code ${code}\n`);
      this.rejectAll(new Error(`Python engine exited (code ${code})`));
      this.process = null;
    });
  }

  stop(): void {
    this.process?.kill();
    this.process = null;
  }

  async call<T = unknown>(method: string, params: Record<string, unknown> = {}): Promise<T> {
    if (!this.process) this.start();

    const id = this.nextId++;
    const request: RpcRequest = { id, method, params };
    const body = JSON.stringify(request);
    const frame = `Content-Length: ${Buffer.byteLength(body)}\r\n\r\n${body}`;

    return new Promise<T>((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`Python bridge timeout for method: ${method}`));
      }, REQUEST_TIMEOUT_MS);

      this.pending.set(id, {
        resolve: resolve as (v: unknown) => void,
        reject,
        timer,
      });

      this.process!.stdin!.write(frame);
    });
  }

  private drainBuffer(): void {
    while (true) {
      const headerEnd = this.buffer.indexOf("\r\n\r\n");
      if (headerEnd === -1) break;

      const header = this.buffer.slice(0, headerEnd).toString();
      const match = header.match(/Content-Length:\s*(\d+)/i);
      if (!match) break;

      const length = parseInt(match[1], 10);
      const bodyStart = headerEnd + 4;

      if (this.buffer.length < bodyStart + length) break;

      const body = this.buffer.slice(bodyStart, bodyStart + length).toString();
      this.buffer = this.buffer.slice(bodyStart + length);

      try {
        const msg: RpcResponse = JSON.parse(body);
        this.dispatch(msg);
      } catch {
        // malformed message — skip
      }
    }
  }

  private dispatch(msg: RpcResponse): void {
    if (msg.id === null || msg.id === undefined) return;

    const pending = this.pending.get(msg.id);
    if (!pending) return;

    clearTimeout(pending.timer);
    this.pending.delete(msg.id);

    if (msg.error) {
      pending.reject(new Error(msg.error));
    } else {
      pending.resolve(msg.result);
    }
  }

  private rejectAll(err: Error): void {
    for (const [, pending] of this.pending) {
      clearTimeout(pending.timer);
      pending.reject(err);
    }
    this.pending.clear();
  }
}
