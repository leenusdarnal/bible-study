declare global {
  namespace App {
    interface Platform {
      env: {
        DB: {
          prepare(query: string): {
            bind(...values: unknown[]): {
              all<T = Record<string, unknown>>(): Promise<{ results: T[] }>;
            };
          };
        };
      };
    }
  }
}

export {};
