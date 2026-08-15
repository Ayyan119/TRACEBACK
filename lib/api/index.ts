import { ApiClient } from './client';
import { MockApiClient } from './mock-client';
import { FastApiClient } from './fastapi-client';

const apiMode = process.env.NEXT_PUBLIC_API_MODE || 'mock';

export const api: ApiClient = apiMode === 'real' ? new FastApiClient() : new MockApiClient();

export * from './client';
