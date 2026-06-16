let lastCapturedError: unknown;

export function captureError(error: unknown) {
  lastCapturedError = error;
}

export function consumeLastCapturedError() {
  const error = lastCapturedError;
  lastCapturedError = undefined;
  return error;
}
