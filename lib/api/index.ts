import { ApiClient } from './client';
import { MockApiClient } from './mock-client';
import { FastApiClient } from './fastapi-client';

const apiMode = process.env.NEXT_PUBLIC_API_MODE || 'real';

export const api: ApiClient = apiMode === 'mock' ? new MockApiClient() : new FastApiClient();

export * from './client';
