import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def build_issue(priority, message, impact):
    return {
        "priority": priority,
        "message": message,
        "impact": impact
    }


async def analyze_url(url):

    async with httpx.AsyncClient(
        timeout=10,
        follow_redirects=True,
        headers={"User-Agent": "SEO Analyzer Bot"}
    ) as client:

        response = await client.get(str(url))

        soup = BeautifulSoup(response.text, "lxml")

        # ---------------- SEO BASICS ----------------

        title = soup.title.text.strip() if soup.title else None

        meta = soup.find("meta", attrs={"name": "description"})
        meta_description = (
            meta["content"].strip()
            if meta and meta.get("content")
            else None
        )

        h1 = [h.get_text(strip=True) for h in soup.find_all("h1")]
        h2 = [h.get_text(strip=True) for h in soup.find_all("h2")]

        # ---------------- CLEAN TEXT ----------------

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        words = [
            w for w in soup.get_text(" ").split()
            if len(w) > 1
        ]

        word_count = len(words)

        avg_word_length = (
            sum(len(w) for w in words) / len(words)
            if words else 0
        )

        # ---------------- MEDIA ----------------

        images = soup.find_all("img")
        images_without_alt = sum(
            1 for img in images
            if not img.get("alt")
        )

        # ---------------- LINKS ----------------

        parsed = urlparse(str(response.url))
        domain = parsed.netloc

        internal_links = 0
        external_links = 0

        for a in soup.find_all("a", href=True):

            href = a["href"]

            if href.startswith("/") or domain in href:
                internal_links += 1

            elif href.startswith("http"):
                external_links += 1

        # ---------------- TECHNICAL SEO ----------------

        canonical = soup.find("link", rel="canonical")
        canonical_url = canonical.get("href") if canonical else None

        title_length = len(title) if title else 0
        meta_length = len(meta_description) if meta_description else 0

        og_title = soup.find("meta", property="og:title")
        og_description = soup.find("meta", property="og:description")
        og_image = soup.find("meta", property="og:image")

        twitter_card = soup.find(
            "meta",
            attrs={"name": "twitter:card"}
        )

        base_url = f"{parsed.scheme}://{parsed.netloc}"

        robots_exists = False
        sitemap_exists = False

        try:
            robots = await client.get(f"{base_url}/robots.txt")
            robots_exists = robots.status_code == 200
        except Exception:
            pass

        try:
            sitemap = await client.get(f"{base_url}/sitemap.xml")
            sitemap_exists = sitemap.status_code == 200
        except Exception:
            pass

        # ---------------- SEO SCORE ----------------

        seo_score = 100
        seo_issues = []

        if not title:
            seo_score -= 20
            seo_issues.append(build_issue(
                "high",
                "Missing title tag",
                20
            ))

        elif title_length < 30:
            seo_score -= 5
            seo_issues.append(build_issue(
                "medium",
                "Title too short",
                5
            ))

        elif title_length > 60:
            seo_score -= 5
            seo_issues.append(build_issue(
                "medium",
                "Title too long",
                5
            ))

        if not meta_description:
            seo_score -= 15
            seo_issues.append(build_issue(
                "high",
                "Missing meta description",
                15
            ))

        elif meta_length < 120:
            seo_score -= 5
            seo_issues.append(build_issue(
                "medium",
                "Meta description too short",
                5
            ))

        if len(h1) == 0:
            seo_score -= 20
            seo_issues.append(build_issue(
                "high",
                "Missing H1",
                20
            ))

        if word_count < 300:
            seo_score -= 15
            seo_issues.append(build_issue(
                "medium",
                "Thin content",
                15
            ))

        if not canonical_url:
            seo_score -= 5
            seo_issues.append(build_issue(
                "low",
                "Missing canonical URL",
                5
            ))

        if not robots_exists:
            seo_score -= 5
            seo_issues.append(build_issue(
                "low",
                "Missing robots.txt",
                5
            ))

        if not sitemap_exists:
            seo_score -= 5
            seo_issues.append(build_issue(
                "low",
                "Missing sitemap.xml",
                5
            ))

        # ---------------- GSEO SCORE ----------------

        gseo_score = 100
        gseo_issues = []

        if word_count < 500:
            gseo_score -= 25
            gseo_issues.append(build_issue(
                "high",
                "Content too thin for AI",
                25
            ))

        if len(h2) == 0:
            gseo_score -= 10
            gseo_issues.append(build_issue(
                "medium",
                "No H2 headings",
                10
            ))

        if avg_word_length < 4:
            gseo_score -= 10
            gseo_issues.append(build_issue(
                "low",
                "Writing style is simplistic",
                10
            ))

        # ---------------- ACTION PLAN ----------------

        actions = []

        if not title:
            actions.append({
                "priority": "critical",
                "action": "Add a title tag between 50 and 60 characters.",
                "impact": "Improves rankings and click-through rate."
            })

        if not meta_description:
            actions.append({
                "priority": "critical",
                "action": "Add a meta description between 140 and 160 characters.",
                "impact": "Improves click-through rate from search engines."
            })

        if word_count < 500:
            actions.append({
                "priority": "high",
                "action": "Increase content to at least 500 words.",
                "impact": "Improves topical authority."
            })

        if images_without_alt > 0:
            actions.append({
                "priority": "medium",
                "action": f"Add ALT text to {images_without_alt} images.",
                "impact": "Improves accessibility and image SEO."
            })

        if not robots_exists:
            actions.append({
                "priority": "medium",
                "action": "Create a robots.txt file.",
                "impact": "Improves crawling."
            })

        if not sitemap_exists:
            actions.append({
                "priority": "medium",
                "action": "Create a sitemap.xml file.",
                "impact": "Improves indexing."
            })

        # ---------------- RETURN ----------------

        return {

            "url": str(response.url),

            "seo": {
                "score": max(seo_score, 0),
                "issues": seo_issues
            },

            "gseo": {
                "score": max(gseo_score, 0),
                "issues": gseo_issues,
                "avg_word_length": round(avg_word_length, 2)
            },

            "content": {
                "title": title,
                "title_length": title_length,
                "meta_description": meta_description,
                "meta_length": meta_length,
                "h1": h1,
                "h2": h2,
                "word_count": word_count
            },

            "media": {
                "images": len(images),
                "images_without_alt": images_without_alt
            },

            "links": {
                "internal": internal_links,
                "external": external_links
            },

            "technical": {
                "canonical": canonical_url,
                "robots_txt": robots_exists,
                "sitemap_xml": sitemap_exists,
                "og_title": bool(og_title),
                "og_description": bool(og_description),
                "og_image": bool(og_image),
                "twitter_card": bool(twitter_card)
            },

            "actions": actions
        }