function color(score) {
    if (score >= 80) return "#22c55e";
    if (score >= 50) return "#facc15";
    return "#ef4444";
}

function normalizeUrl(url) {

    if (!url) return null;

    url = url.trim();

    if (
        !url.startsWith("http://") &&
        !url.startsWith("https://")
    ) {
        url = "https://" + url;
    }

    return url;
}

function showDashboard() {

    document
        .getElementById("dashboardPanel")
        .classList.remove("hidden");

    document
        .getElementById("historyPanel")
        .classList.add("hidden");

}

function showHistory() {

    document
        .getElementById("dashboardPanel")
        .classList.add("hidden");

    document
        .getElementById("historyPanel")
        .classList.remove("hidden");

    loadHistory();

}

function toggleSidebar() {

    document
        .getElementById("sidebar")
        .classList.toggle("open");

}

async function analyze() {

    const rawUrl = document.getElementById("url").value;
    const url = normalizeUrl(rawUrl);

    if (!url) {
        alert("Please enter a URL.");
        return;
    }

    showDashboard();

    const result = document.getElementById("result");

    result.innerHTML = `
        <h3>Analyzing...</h3>
        <p>Please wait...</p>
    `;

    try {

        const res = await fetch("/analyze", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                url
            })

        });

        if (!res.ok) {
            throw new Error("Server error");
        }

        const data = await res.json();

        // KPI

        document.getElementById("seoScore").innerText =
            data.seo.score;

        document.getElementById("gseoScore").innerText =
            data.gseo.score;

        document.getElementById("words").innerText =
            data.content.word_count;

        document.getElementById("images").innerText =
            data.media.images_without_alt;

        document.getElementById("seoScore").style.color =
            color(data.seo.score);

        document.getElementById("gseoScore").style.color =
            color(data.gseo.score);

        // ACTIONS

        const actions = (data.actions || []).map(a => `

            <div class="audit-card">

                <div class="audit-priority ${a.priority}">
                    ${a.priority.toUpperCase()}
                </div>

                <div>

                    <strong>${a.action}</strong>

                    <p>${a.impact}</p>

                </div>

            </div>

        `).join("");

        // TECHNICAL

        const tech = data.technical || {};

        result.innerHTML = `

            <h2>SEO Audit</h2>

            <h3>Priority Actions</h3>

            ${actions || "<p>No recommendations.</p>"}

            <hr>

            <h3>Technical SEO</h3>

            <table class="tech-table">

                <tr>
                    <td>Canonical</td>
                    <td>${tech.canonical || "❌ Missing"}</td>
                </tr>

                <tr>
                    <td>Robots.txt</td>
                    <td>${tech.robots_txt ? "✅" : "❌"}</td>
                </tr>

                <tr>
                    <td>Sitemap.xml</td>
                    <td>${tech.sitemap_xml ? "✅" : "❌"}</td>
                </tr>

                <tr>
                    <td>Open Graph Title</td>
                    <td>${tech.og_title ? "✅" : "❌"}</td>
                </tr>

                <tr>
                    <td>Open Graph Description</td>
                    <td>${tech.og_description ? "✅" : "❌"}</td>
                </tr>

                <tr>
                    <td>Open Graph Image</td>
                    <td>${tech.og_image ? "✅" : "❌"}</td>
                </tr>

                <tr>
                    <td>Twitter Card</td>
                    <td>${tech.twitter_card ? "✅" : "❌"}</td>
                </tr>

            </table>

        `;

        loadHistory();

    }

    catch (err) {

        console.error(err);

        result.innerHTML = `

            <h3>Error</h3>

            <p>
                Unable to analyze this website.
            </p>

        `;

    }

}

async function loadHistory() {

    try {

        const res = await fetch("/history");

        const data = await res.json();

        document.getElementById("historyList").innerHTML =
            data.map(item => `

                <div
                    class="history-item"
                    onclick="openHistory('${item.url}')">

                    <strong>${item.url}</strong>

                    <br>

                    SEO ${item.seo_score}

                    |

                    GSEO ${item.gseo_score}

                </div>

            `).join("");

    }

    catch (err) {

        console.error(err);

    }

}

function openHistory(url) {

    document.getElementById("url").value = url;

    showDashboard();

    analyze();

}

window.addEventListener("DOMContentLoaded", () => {

    showDashboard();

    loadHistory();

});