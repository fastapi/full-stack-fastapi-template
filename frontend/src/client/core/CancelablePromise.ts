export class CancelError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "CancelError";
  }

  public get isCancelled(): boolean {
    return true;
  }
}

export interface OnCancel {
  readonly isResolved: boolean;
  readonly isRejected: boolean;
  readonly isCancelled: boolean;

  (cancelHandler: () => void): void;
}

export class CancelablePromise<T> implements Promise<T> {
  private _isResolved: boolean = false;
  private _isRejected: boolean = false;
  private _isCancelled: boolean = false;
  private readonly cancelHandlers: (() => void)[] = [];
  private readonly promise: Promise<T>;
  private _resolve?: (value: T | PromiseLike<T>) => void;
  private _reject?: (reason?: unknown) => void;

  constructor(
    executor: (
      resolve: (value: T | PromiseLike<T>) => void,
      reject: (reason?: unknown) => void,
      onCancel: OnCancel,
    ) => void,
  ) {
    this.promise = new Promise<T>((resolve, reject) => {
      this._resolve = resolve;
      this._reject = reject;

      const onCancel = this.createOnCancel();

      executor(this.createResolve(), this.createReject(), onCancel);
    });
  }

  private createResolve(): (value: T | PromiseLike<T>) => void {
    return (value: T | PromiseLike<T>): void => {
      if (this.isFinalState()) return;
      this._isResolved = true;
      this._resolve?.(value);
    };
  }

  private createReject(): (reason?: unknown) => void {
    return (reason?: unknown): void => {
      if (this.isFinalState()) return;
      this._isRejected = true;
      this._reject?.(reason);
    };
  }

  private createOnCancel(): OnCancel {
    const onCancel = ((cancelHandler: () => void): void => {
      if (this.isFinalState()) return;
      this.cancelHandlers.push(cancelHandler);
    }) as OnCancel;

    Object.defineProperties(onCancel, {
      isResolved: { get: () => this._isResolved },
      isRejected: { get: () => this._isRejected },
      isCancelled: { get: () => this._isCancelled },
    });

    return onCancel;
  }

  private isFinalState(): boolean {
    return this._isResolved || this._isRejected || this._isCancelled;
  }

  get [Symbol.toStringTag]() {
    return "Cancellable Promise";
  }

  public then<TResult1 = T, TResult2 = never>(
    onFulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | null,
    onRejected?: ((reason: unknown) => TResult2 | PromiseLike<TResult2>) | null,
  ): Promise<TResult1 | TResult2> {
    return this.promise.then(onFulfilled, onRejected);
  }

  public catch<TResult = never>(
    onRejected?: ((reason: unknown) => TResult | PromiseLike<TResult>) | null,
  ): Promise<T | TResult> {
    return this.promise.catch(onRejected);
  }

  public finally(onFinally?: (() => void) | null): Promise<T> {
    return this.promise.finally(onFinally);
  }

  public cancel(): void {
    if (this.isFinalState()) return;

    this._isCancelled = true;

    try {
      for (const cancelHandler of this.cancelHandlers) {
        cancelHandler();
      }
    } catch (error) {
      console.error("Error during cancellation:", error);
    } finally {
      this.cancelHandlers.length = 0;
      this._reject?.(new CancelError("Request aborted"));
    }
  }

  public get isCancelled(): boolean {
    return this._isCancelled;
  }
}
