<?php

namespace App\Services;

use GuzzleHttp\Client;
use GuzzleHttp\Exception\GuzzleException;
use GuzzleHttp\Exception\RequestException;
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
}
