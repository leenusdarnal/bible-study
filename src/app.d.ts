declare global {
  namespace App {
    interface Platform {
      env: {
        DB: {
          prepare(query: string): {
            all<T = Record<string, unknown>>(): Promise<{ results: T[] }>;
          };
        };
      };
    }
  }
}

export {};
