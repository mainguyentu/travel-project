<?php

namespace App\Services;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;
use GuzzleHttp\Exception\RequestException;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Session;
use Exception;

class ApiClient
{
    private Client $client;
    private string $baseUrl;
    private string $apiVersion;

    public function __construct()
    {
        $this->baseUrl = config('api.base_url');
        $this->apiVersion = config('api.version');
        
        $this->client = new Client([
            'base_uri' => $this->baseUrl,
            'timeout' => config('api.timeout', 30),
            'verify' => config('api.verify_ssl', true),
        ]);
    }

    /**
     * Get the full endpoint URL
     */
    private function getEndpoint(string $path): string
    {
        return "/api/{$this->apiVersion}/{$path}";
    }

    /**
     * Get headers with authorization
     */
    private function getHeaders(): array
    {
        $headers = [
            'Accept' => 'application/json',
            'Content-Type' => 'application/json',
        ];

        // Add authorization token if exists
        if ($token = Session::get('access_token')) {
            $headers['Authorization'] = "Bearer {$token}";
        }

        return $headers;
    }

    /**
     * GET request
     */
    public function get(string $path, array $query = []): array
    {
        if (!$this->shouldUseCache($path)) {
            return $this->performGet($path, $query);
        }

        $store = Cache::store($this->getCacheStore());
        $cacheKey = $this->buildCacheKey($path, $query);
        $cached = $store->get($cacheKey);

        if (is_array($cached)) {
            return $cached;
        }

        $response = $this->performGet($path, $query);

        if (($response['success'] ?? true) !== false) {
            $store->put($cacheKey, $response, now()->addSeconds($this->getCacheTtl($path)));
            $this->registerCacheKey($cacheKey);
        }

        return $response;
    }

    /**
     * GET request without cache
     */
    private function performGet(string $path, array $query = []): array
    {
        try {
            $response = $this->client->get($this->getEndpoint($path), [
                'headers' => $this->getHeaders(),
                'query' => $query,
            ]);

            return json_decode($response->getBody()->getContents(), true);
        } catch (GuzzleException $e) {
            return $this->handleError($e);
        }
    }

    /**
     * POST request
     */
    public function post(string $path, array $data = []): array
    {
        try {
            $response = $this->client->post($this->getEndpoint($path), [
                'headers' => $this->getHeaders(),
                'json' => $data,
            ]);

            $this->invalidateCacheOnWrite();

            return json_decode($response->getBody()->getContents(), true);
        } catch (GuzzleException $e) {
            return $this->handleError($e);
        }
    }

    /**
     * PUT request
     */
    public function put(string $path, array $data = []): array
    {
        try {
            $response = $this->client->put($this->getEndpoint($path), [
                'headers' => $this->getHeaders(),
                'json' => $data,
            ]);

            $this->invalidateCacheOnWrite();

            return json_decode($response->getBody()->getContents(), true);
        } catch (GuzzleException $e) {
            return $this->handleError($e);
        }
    }

    /**
     * DELETE request
     */
    public function delete(string $path): array
    {
        try {
            $response = $this->client->delete($this->getEndpoint($path), [
                'headers' => $this->getHeaders(),
            ]);

            $this->invalidateCacheOnWrite();

            return json_decode($response->getBody()->getContents(), true);
        } catch (GuzzleException $e) {
            return $this->handleError($e);
        }
    }

    /**
     * Handle API errors
     */
    private function handleError(GuzzleException $e): array
    {
        $response = $e instanceof RequestException ? $e->getResponse() : null;
        $statusCode = $response?->getStatusCode() ?? 500;
        $body = $response?->getBody()->getContents() ?? '';

        try {
            $decoded = json_decode($body, true) ?? [];
        } catch (Exception) {
            $decoded = ['message' => $body];
        }

        return [
            'success' => false,
            'status' => $statusCode,
            'error' => $decoded['error']['message'] ?? $decoded['message'] ?? 'API Error',
            'details' => $decoded['error']['details'] ?? $decoded,
        ];
    }

    private function shouldUseCache(string $path): bool
    {
        if (!config('api.cache.enabled', true)) {
            return false;
        }

        $hasToken = Session::has('access_token');
        if ($hasToken && !config('api.cache.cache_authenticated', false)) {
            return false;
        }

        $prefixes = $hasToken
            ? config('api.cache.authenticated_path_prefixes', [])
            : config('api.cache.public_path_prefixes', []);

        if (!is_array($prefixes) || $prefixes === []) {
            return false;
        }

        foreach ($prefixes as $prefix) {
            if (str_starts_with($path, $prefix)) {
                return true;
            }
        }

        return false;
    }

    private function buildCacheKey(string $path, array $query): string
    {
        $normalizedQuery = $this->normalizeQuery($query);
        $payload = $path;
        if ($normalizedQuery !== []) {
            $payload .= '?' . http_build_query($normalizedQuery);
        }

        return config('api.cache.key_prefix', 'frontend:api-response') . ':' . sha1($payload);
    }

    private function normalizeQuery(array $query): array
    {
        ksort($query);

        foreach ($query as $key => $value) {
            if (is_array($value)) {
                $query[$key] = $this->normalizeQuery($value);
            }
        }

        return $query;
    }

    private function getCacheTtl(string $path): int
    {
        $pathTtls = config('api.cache.path_ttl', []);
        if (is_array($pathTtls)) {
            foreach ($pathTtls as $prefix => $ttl) {
                if (str_starts_with($path, $prefix)) {
                    return max((int) $ttl, 1);
                }
            }
        }

        return max((int) config('api.cache.default_ttl', 120), 1);
    }

    private function getCacheStore(): string
    {
        return (string) config('api.cache.store', 'redis');
    }

    private function getRegistryKey(): string
    {
        return (string) config('api.cache.registry_key', 'frontend:api-response:keys');
    }

    private function registerCacheKey(string $cacheKey): void
    {
        $store = Cache::store($this->getCacheStore());
        $registryKey = $this->getRegistryKey();
        $keys = $store->get($registryKey, []);

        if (!is_array($keys)) {
            $keys = [];
        }

        if (!in_array($cacheKey, $keys, true)) {
            $keys[] = $cacheKey;
            $store->forever($registryKey, $keys);
        }
    }

    private function invalidateCacheOnWrite(): void
    {
        if (!config('api.cache.invalidate_on_write', true)) {
            return;
        }

        $store = Cache::store($this->getCacheStore());
        $registryKey = $this->getRegistryKey();
        $keys = $store->pull($registryKey, []);

        if (!is_array($keys)) {
            return;
        }

        foreach ($keys as $cacheKey) {
            if (is_string($cacheKey) && $cacheKey !== '') {
                $store->forget($cacheKey);
            }
        }
    }
}
