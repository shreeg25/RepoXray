<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RepoScribe: AI-Powered Project README Generator</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* Custom styling for inline code to match standard markdown rendering */
        code:not(pre code) {
            background-color: #f3f4f6;
            padding: 0.2rem 0.4rem;
            border-radius: 0.25rem;
            font-size: 0.875em;
            color: #ef4444;
        }
    </style>
</head>
<body class="bg-gray-50 text-gray-800 font-sans antialiased p-4 md:p-8 lg:p-12">

    <div class="max-w-4xl mx-auto bg-white p-6 md:p-10 rounded-xl shadow-lg">
        
        <!-- Header Section -->
        <header class="mb-8">
            <h1 class="text-3xl md:text-4xl font-extrabold text-gray-900 tracking-tight mb-4">
                🤖 RepoScribe: AI-Powered Project README Generator
            </h1>
            <p class="text-lg text-gray-600 leading-relaxed">
                RepoScribe is an intelligent AI agent built for the <strong>Epoch X Nasiko Hackathon</strong>. It automatically scans complex codebases, parses directory structures, and leverages Large Language Models (Gemini 2.5) to generate comprehensive, highly accurate <code>README.md</code> files.
            </p>
        </header>

        <!-- Architecture Section -->
        <section class="mb-10">
            <h2 class="text-2xl font-bold text-gray-900 border-b-2 border-gray-200 pb-2 mb-4">
                🏗️ Agent Design & Architecture
            </h2>
            <p class="mb-4 text-gray-700">
                This agent utilizes a <strong>Map-Reduce Architecture</strong> combined with <strong>Concurrent Processing</strong> to efficiently handle large repositories without exceeding LLM context windows or API rate limits.
            </p>
            <ol class="list-decimal pl-6 space-y-3 text-gray-700">
                <li>
                    <strong>File Reader Tool (<code>tools.py</code>)</strong>: Traverses the project directory. It safely ignores binaries, parses <code>.gitignore</code> rules, and skips empty files to optimize token usage.
                </li>
                <li>
                    <strong>Map Step (Multithreading)</strong>: Uses <code>concurrent.futures</code> to analyze up to 3 files simultaneously, generating bite-sized 2-3 sentence summaries for each file.
                </li>
                <li>
                    <strong>Reduce Step</strong>: Aggregates all file summaries and the generated folder tree into a final prompt, instructing the LLM to write a cohesive, professional Markdown document.
                </li>
                <li>
                    <strong>Resiliency</strong>: Integrates <code>tenacity</code> for Exponential Backoff. If the API rate limits the agent (429 Quota Exceeded), it automatically pauses and retries, ensuring stability on large folders.
                </li>
            </ol>
        </section>

        <!-- Usage Instructions Section -->
        <section class="mb-10">
            <h2 class="text-2xl font-bold text-gray-900 border-b-2 border-gray-200 pb-2 mb-4">
                🚀 Usage Instructions
            </h2>

            <h3 class="text-xl font-semibold text-gray-800 mt-6 mb-3">Prerequisites</h3>
            <ul class="list-disc pl-6 space-y-1 text-gray-700 mb-6">
                <li>Python 3.8+</li>
                <li>A Google Gemini API Key</li>
            </ul>

            <h3 class="text-xl font-semibold text-gray-800 mt-6 mb-3">Setup</h3>
            <ol class="list-decimal pl-6 space-y-4 text-gray-700 mb-6">
                <li>
                    Clone this repository:
                    <pre class="bg-gray-900 text-gray-100 p-4 rounded-lg mt-2 overflow-x-auto text-sm"><code>git clone &lt;your-repo-link&gt;
cd &lt;your-repo-folder&gt;</code></pre>
                </li>
                <li>
                    Install dependencies:
                    <pre class="bg-gray-900 text-gray-100 p-4 rounded-lg mt-2 overflow-x-auto text-sm"><code>pip install -r requirements.txt</code></pre>
                </li>
                <li>
                    Set up your environment variables. Create a <code>.env</code> file in the root directory:
                    <pre class="bg-gray-900 text-gray-100 p-4 rounded-lg mt-2 overflow-x-auto text-sm"><code>GOOGLE_API_KEY=your_gemini_api_key_here</code></pre>
                </li>
            </ol>

            <h3 class="text-xl font-semibold text-gray-800 mt-6 mb-3">Running the Agent</h3>
            <p class="mb-2 text-gray-700">To generate a README for the current directory:</p>
            <pre class="bg-gray-900 text-gray-100 p-4 rounded-lg mb-4 overflow-x-auto text-sm"><code>python -m app .</code></pre>
            
            <p class="mb-2 text-gray-700">To generate a README for a different project folder:</p>
            <pre class="bg-gray-900 text-gray-100 p-4 rounded-lg mb-6 overflow-x-auto text-sm"><code>python -m app /path/to/target/project</code></pre>
        </section>

        <!-- Assumptions & Limitations Section -->
        <section>
            <h2 class="text-2xl font-bold text-gray-900 border-b-2 border-gray-200 pb-2 mb-4">
                ⚠️ Assumptions & Limitations
            </h2>
            <ul class="list-disc pl-6 space-y-3 text-gray-700">
                <li>
                    <strong>API Quotas:</strong> The agent assumes the use of a free-tier Gemini API key. It is intentionally throttled (using <code>time.sleep</code> and limited thread workers) to avoid hitting the strict 15 Requests/Minute limit.
                </li>
                <li>
                    <strong>Token Limits:</strong> While the Map-Reduce architecture drastically reduces token bloat, a project with hundreds of massive source files could theoretically still exceed the final <code>Reduce</code> prompt's context window.
                </li>
                <li>
                    <strong>Binary Files:</strong> The agent assumes standard file extensions for binaries (<code>.png</code>, <code>.exe</code>, etc.). Unknown binary types lacking an extension might be read as text, though a <code>UnicodeDecodeError</code> fallback is implemented to catch most of these.
                </li>
            </ul>
        </section>

    </div>

</body>
</html>