/**
 * Mini CRM Frontend JavaScript
 * Fetch helpers for API calls
 */

const api = {
    /**
     * Base fetch wrapper with JSON handling
     */
    async request(url, options = {}) {
        const defaults = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        const config = { ...defaults, ...options };

        const response = await fetch(url, config);

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Request failed' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        if (response.status === 204) {
            return null;
        }

        return response.json();
    },

    get(url) {
        return this.request(url);
    },

    post(url, data) {
        return this.request(url, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    put(url, data) {
        return this.request(url, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    patch(url, data) {
        return this.request(url, {
            method: 'PATCH',
            body: JSON.stringify(data),
        });
    },

    delete(url) {
        return this.request(url, {
            method: 'DELETE',
        });
    },
};
