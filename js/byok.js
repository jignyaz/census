/**
 * BYOK (Bring Your Own Key) Client-Side Service Module
 * Implements local storage management, Direct LLM integrations (Gemini & Groq), 
 * connection validation, and error translation.
 */

const BYOK_ERRORS = {
    NO_API_KEY: 'NO_API_KEY',
    INVALID_API_KEY: 'INVALID_API_KEY',
    RATE_LIMITED: 'RATE_LIMITED',
    NETWORK_ERROR: 'NETWORK_ERROR',
    GENERIC_ERROR: 'GENERIC_ERROR'
};

class BYOKStorage {
    static getProvider() {
        return localStorage.getItem('byok_provider') || 'gemini';
    }

    static setProvider(provider) {
        localStorage.setItem('byok_provider', provider);
    }

    static getKey(provider) {
        return localStorage.getItem(`byok_${provider}_key`) || '';
    }

    static saveKey(provider, key) {
        localStorage.setItem(`byok_${provider}_key`, key.trim());
    }

    static deleteKey(provider) {
        localStorage.removeItem(`byok_${provider}_key`);
    }

    static getModel(provider) {
        if (provider === 'gemini') {
            return localStorage.getItem('byok_gemini_model') || 'gemini-2.0-flash';
        } else {
            return localStorage.getItem('byok_groq_model') || 'mixtral-8x7b-32768';
        }
    }

    static setModel(provider, model) {
        localStorage.setItem(`byok_${provider}_model`, model.trim());
    }

    static getEndpoint(provider) {
        if (provider === 'groq') {
            return localStorage.getItem('byok_groq_endpoint') || 'https://api.groq.com/openai/v1';
        }
        return '';
    }

    static setEndpoint(provider, url) {
        if (provider === 'groq') {
            localStorage.setItem('byok_groq_endpoint', url.trim());
        }
    }

    static isEnabled() {
        return localStorage.getItem('byok_enabled') === 'true';
    }

    static setEnabled(enabled) {
        localStorage.setItem('byok_enabled', enabled ? 'true' : 'false');
    }
}

class GeminiClient {
    constructor(apiKey, modelName = 'gemini-2.0-flash') {
        this.apiKey = apiKey;
        this.modelName = modelName;
    }

    async testConnection() {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.modelName}:generateContent?key=${this.apiKey}`;
        const payload = {
            contents: [{ parts: [{ text: "Respond with 'connected' in exactly 1 word." }] }],
            generationConfig: { maxOutputTokens: 5, temperature: 0 }
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    throw new Error(BYOK_ERRORS.INVALID_API_KEY);
                }
                if (response.status === 429) {
                    throw new Error(BYOK_ERRORS.RATE_LIMITED);
                }
                throw new Error(BYOK_ERRORS.GENERIC_ERROR);
            }

            const data = await response.json();
            if (data.error) {
                const code = data.error.code;
                if (code === 401 || code === 403) throw new Error(BYOK_ERRORS.INVALID_API_KEY);
                if (code === 429) throw new Error(BYOK_ERRORS.RATE_LIMITED);
                throw new Error(BYOK_ERRORS.GENERIC_ERROR);
            }
            return true;
        } catch (err) {
            if (err.message === BYOK_ERRORS.INVALID_API_KEY || err.message === BYOK_ERRORS.RATE_LIMITED) {
                throw err;
            }
            throw new Error(BYOK_ERRORS.NETWORK_ERROR);
        }
    }

    async generateSQL(question) {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.modelName}:generateContent?key=${this.apiKey}`;
        const systemPrompt = `You are a census data analyst for an Indian government socioeconomic survey. You have access to a SQLite database called census.db with one table called 'census' with these exact columns:
id, census_house_number, floor_material, wall_material, ceiling_material, building_usage, building_condition, number_of_people, head_of_family_name, gender, rooms, married_pairs, drinking_water_source, water_source_location, light_source, sanitation_facilities, rest_room, sewage_flow, bathing_facilities, cooking_gas, cooking_fuel, radio, tv, internet, laptop_computer, transportation, primary_food, phone_number, registered_at.

Respond ONLY with a valid SQLite SQL query. No explanation. No markdown. No backticks. Just the raw SQL query on one line.`;

        const payload = {
            contents: [{ parts: [{ text: question }] }],
            systemInstruction: { parts: [{ text: systemPrompt }] },
            generationConfig: { temperature: 0.1, maxOutputTokens: 300 }
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) throw new Error(BYOK_ERRORS.INVALID_API_KEY);
                if (response.status === 429) throw new Error(BYOK_ERRORS.RATE_LIMITED);
                throw new Error(BYOK_ERRORS.GENERIC_ERROR);
            }

            const data = await response.json();
            if (data.error) {
                const code = data.error.code;
                if (code === 401 || code === 403) throw new Error(BYOK_ERRORS.INVALID_API_KEY);
                if (code === 429) throw new Error(BYOK_ERRORS.RATE_LIMITED);
                throw new Error(data.error.message || BYOK_ERRORS.GENERIC_ERROR);
            }

            const text = data.candidates[0].content.parts[0].text;
            return cleanSQL(text);
        } catch (err) {
            if (err.message === BYOK_ERRORS.INVALID_API_KEY || err.message === BYOK_ERRORS.RATE_LIMITED) {
                throw err;
            }
            throw new Error(BYOK_ERRORS.NETWORK_ERROR);
        }
    }

    async humanizeResult(question, sqlQuery, dbResults) {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.modelName}:generateContent?key=${this.apiKey}`;
        const systemPrompt = "You are a helpful socioeconomic survey analyst for the Indian government.";
        const userMsg = `The user asked: ${question}
The SQL query was: ${sqlQuery}
The SQL query result was: ${JSON.stringify(dbResults)}
Write a clear friendly human-readable answer in 1-2 sentences. Be specific with numbers. If result is empty say no records found.`;

        const payload = {
            contents: [{ parts: [{ text: userMsg }] }],
            systemInstruction: { parts: [{ text: systemPrompt }] },
            generationConfig: { temperature: 0.3, maxOutputTokens: 300 }
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) throw new Error(BYOK_ERRORS.INVALID_API_KEY);
                if (response.status === 429) throw new Error(BYOK_ERRORS.RATE_LIMITED);
                throw new Error(BYOK_ERRORS.GENERIC_ERROR);
            }

            const data = await response.json();
            const text = data.candidates[0].content.parts[0].text;
            return text.trim();
        } catch (err) {
            if (err.message === BYOK_ERRORS.INVALID_API_KEY || err.message === BYOK_ERRORS.RATE_LIMITED) {
                throw err;
            }
            throw new Error(BYOK_ERRORS.NETWORK_ERROR);
        }
    }
}

class GroqClient {
    constructor(apiKey, endpoint = 'https://api.groq.com/openai/v1', modelName = 'mixtral-8x7b-32768') {
        this.apiKey = apiKey;
        this.endpoint = endpoint.replace(/\/$/, ''); // Remove trailing slash if present
        this.modelName = modelName;
    }

    async testConnection() {
        const url = `${this.endpoint}/chat/completions`;
        const payload = {
            model: this.modelName,
            messages: [{ role: 'user', content: "Respond with 'connected' in exactly 1 word." }],
            max_tokens: 5,
            temperature: 0
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) {
                    throw new Error(BYOK_ERRORS.INVALID_API_KEY);
                }
                if (response.status === 429) {
                    throw new Error(BYOK_ERRORS.RATE_LIMITED);
                }
                throw new Error(BYOK_ERRORS.GENERIC_ERROR);
            }

            return true;
        } catch (err) {
            if (err.message === BYOK_ERRORS.INVALID_API_KEY || err.message === BYOK_ERRORS.RATE_LIMITED) {
                throw err;
            }
            throw new Error(BYOK_ERRORS.NETWORK_ERROR);
        }
    }

    async generateSQL(question) {
        const url = `${this.endpoint}/chat/completions`;
        const systemPrompt = `You are a census data analyst for an Indian government socioeconomic survey. You have access to a SQLite database called census.db with one table called 'census' with these exact columns:
id, census_house_number, floor_material, wall_material, ceiling_material, building_usage, building_condition, number_of_people, head_of_family_name, gender, rooms, married_pairs, drinking_water_source, water_source_location, light_source, sanitation_facilities, rest_room, sewage_flow, bathing_facilities, cooking_gas, cooking_fuel, radio, tv, internet, laptop_computer, transportation, primary_food, phone_number, registered_at.

Respond ONLY with a valid SQLite SQL query. No explanation. No markdown. No backticks. Just the raw SQL query on one line.`;

        const payload = {
            model: this.modelName,
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: question }
            ],
            temperature: 0.1,
            max_tokens: 300
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) throw new Error(BYOK_ERRORS.INVALID_API_KEY);
                if (response.status === 429) throw new Error(BYOK_ERRORS.RATE_LIMITED);
                throw new Error(BYOK_ERRORS.GENERIC_ERROR);
            }

            const data = await response.json();
            const text = data.choices[0].message.content;
            return cleanSQL(text);
        } catch (err) {
            if (err.message === BYOK_ERRORS.INVALID_API_KEY || err.message === BYOK_ERRORS.RATE_LIMITED) {
                throw err;
            }
            throw new Error(BYOK_ERRORS.NETWORK_ERROR);
        }
    }

    async humanizeResult(question, sqlQuery, dbResults) {
        const url = `${this.endpoint}/chat/completions`;
        const systemPrompt = "You are a helpful socioeconomic survey analyst for the Indian government.";
        const userMsg = `The user asked: ${question}
The SQL query was: ${sqlQuery}
The SQL query result was: ${JSON.stringify(dbResults)}
Write a clear friendly human-readable answer in 1-2 sentences. Be specific with numbers. If result is empty say no records found.`;

        const payload = {
            model: this.modelName,
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userMsg }
            ],
            temperature: 0.3,
            max_tokens: 300
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                if (response.status === 401 || response.status === 403) throw new Error(BYOK_ERRORS.INVALID_API_KEY);
                if (response.status === 429) throw new Error(BYOK_ERRORS.RATE_LIMITED);
                throw new Error(BYOK_ERRORS.GENERIC_ERROR);
            }

            const data = await response.json();
            return data.choices[0].message.content.trim();
        } catch (err) {
            if (err.message === BYOK_ERRORS.INVALID_API_KEY || err.message === BYOK_ERRORS.RATE_LIMITED) {
                throw err;
            }
            throw new Error(BYOK_ERRORS.NETWORK_ERROR);
        }
    }
}

/**
 * SQL Cleaner helper: removes backticks, markdown block wrapper, simplifies whitespaces
 */
function cleanSQL(sqlStr) {
    let cleaned = sqlStr.trim();
    if (cleaned.startsWith("```")) {
        const lines = cleaned.split("\n");
        if (lines[0].startsWith("```")) {
            lines.shift();
        }
        if (lines.length > 0 && lines[lines.length - 1].trim() === "```") {
            lines.pop();
        }
        cleaned = lines.join("\n").trim();
    }
    // Remove wrapping single or double backticks
    cleaned = cleaned.replace(/^`+|`+$/g, '').trim();
    // Simplify whitespace and newlines
    cleaned = cleaned.replace(/\n/g, ' ').replace(/\r/g, '');
    while (cleaned.includes("  ")) {
        cleaned = cleaned.replace("  ", " ");
    }
    return cleaned.trim();
}

/**
 * Orchestrator Factory: retrieves settings from localStorage and returns active client
 */
function getBYOKClient() {
    if (!BYOKStorage.isEnabled()) {
        return null;
    }
    const provider = BYOKStorage.getProvider();
    const apiKey = BYOKStorage.getKey(provider);
    if (!apiKey) {
        throw new Error(BYOK_ERRORS.NO_API_KEY);
    }

    const model = BYOKStorage.getModel(provider);
    if (provider === 'gemini') {
        return new GeminiClient(apiKey, model);
    } else {
        const endpoint = BYOKStorage.getEndpoint('groq');
        return new GroqClient(apiKey, endpoint, model);
    }
}
