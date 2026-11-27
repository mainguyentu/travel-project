<?php

namespace App\Services;

use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;

class ApiClient
{
    protected ?string $accessToken;

    protected ?string $refreshToken;

    /** @var callable|null */
    protected $onTokensRefreshed;

    /** @var callable|null */
    protected $onUnauthenticated;

    public function __construct(?string $accessToken = null, ?string $refreshToken = null)
    {
        $this->accessToken = $accessToken;
        $this->refreshToken = $refreshToken;
    }

    public function onTokensRefreshed(callable $cb): static
    {
        $this->onTokensRefreshed = $cb;

        return $this;
    }

    public function onUnauthenticated(callable $cb): static
    {
        $this->onUnauthenticated = $cb;

        return $this;
    }

    public function get(string $path, array $query = []): array
    {
        $key = $this->cacheKey('GET', $path, $query);
        $ttl = $this->ttlFor($path);
        if (config('api.cache.enabled') && $ttl > 0 && $key) {
            return Cache::remember($key, $ttl, fn () => $this->request('GET', $path, ['query' => $query]));
        }

        return $this->request('GET', $path, ['query' => $query]);
    }

    public function post(string $path, array $payload = []): array
    {
        $result = $this->request('POST', $path, ['json' => $payload]);
        $this->invalidate($path);

        return $result;
    }

    public function put(string $path, array $payload = []): array
    {
        $result = $this->request('PUT', $path, ['json' => $payload]);
        $this->invalidate($path);

        return $result;
    }

    public function patch(string $path, array $payload = []): array
    {
        $result = $this->request('PATCH', $path, ['json' => $payload]);
        $this->invalidate($path);

        return $result;
    }

    public function delete(string $path): array
    {
        $result = $this->request('DELETE', $path);
        $this->invalidate($path);

        return $result;
    }

    protected function request(string $method, string $path, array $options = [], bool $retry = true): array
    {
        $response = Http::withHeaders($this->authHeaders())->$method(
            $this->url($path),
            $options['json'] ?? $options['query'] ?? []
        );

        if ($response->status() === 401 && $retry && ! str_starts_with(ltrim($path, '/'), 'auth/')) {
            if ($this->tryRefresh()) {
                return $this->request($method, $path, $options, false);
            }
            if ($this->onUnauthenticated) {
                ($this->onUnauthenticated)();
            }
        }

        $body = $response->json() ?? [];
        $body['_status'] = $response->status();

        return $body;
    }

    protected function tryRefresh(): bool
    {
        if (! $this->refreshToken) {
            return false;
        }
        $response = Http::post($this->url('auth/refresh'), ['refresh_token' => $this->refreshToken]);
        $body = $response->json() ?? [];
        if (! $response->successful() || empty($body['data']['access_token'])) {
            return false;
        }
        $this->accessToken = $body['data']['access_token'];
        $this->refreshToken = $body['data']['refresh_token'] ?? $this->refreshToken;
        if ($this->onTokensRefreshed) {
            ($this->onTokensRefreshed)($this->accessToken, $this->refreshToken);
        }

        return true;
    }

    protected function authHeaders(): array
    {
        return $this->accessToken ? ['Authorization' => 'Bearer '.$this->accessToken] : [];
    }

    protected function url(string $path): string
    {
        return rtrim(config('api.base_url'), '/').'/'.ltrim($path, '/');
    }

    protected function ttlFor(string $path): int
    {
        $p = ltrim($path, '/');
        if (str_starts_with($p, 'public/')) {
            return (int) config('api.cache.ttl.public');
        }
        if (str_starts_with($p, 'destinations')) {
            return (int) config('api.cache.ttl.destinations');
        }

        return (int) config('api.cache.ttl.default');
    }

    protected function cacheKey(string $method, string $path, array $query): ?string
    {
        if ($method !== 'GET') {
            return null;
        }
        $p = ltrim($path, '/');
        if (str_starts_with($p, 'auth/') || str_starts_with($p, 'me/') || str_starts_with($p, 'admin/')) {
            return null;
        }
        ksort($query);

        return 'api:'.md5($p.'?'.http_build_query($query));
    }

    protected function invalidate(string $path): void
    {
        $p = ltrim($path, '/');
        if (str_starts_with($p, 'me/') || str_starts_with($p, 'admin/') || str_starts_with($p, 'destinations')) {
            Cache::flush();
        }
    }
}
