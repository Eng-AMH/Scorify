"""
Scorify — AI Engine
All logic inside functions. Zero module-level state.
"""
import json
import os
import time


def get_client():
    from groq import Groq
    from django.conf import settings
    return Groq(api_key=getattr(settings, 'GROQ_API_KEY', os.getenv('GROQ_API_KEY', '')))


def _lang_rule(language=None):
    if language and language.lower() not in ('english', 'en', ''):
        return (f'LANGUAGE RULE: Write ALL response values in {language}. '
                f'Translate all text. JSON keys stay in English.')
    return 'LANGUAGE RULE: Write all response values in English.'


def _call_groq(prompt: str, max_tokens: int, system: str = None) -> dict:
    client = get_client()
    sys_msg = system or (
        'You are a professional document analyzer. '
        'Return ONLY valid JSON. No markdown fences. No explanation.'
    )
    response = client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages=[
            {'role': 'system', 'content': sys_msg},
            {'role': 'user',   'content': prompt},
        ],
        temperature=0.7,
        max_tokens=max_tokens,
    )
    raw = response.choices[0].message.content.strip()
    if '```' in raw:
        for part in raw.split('```'):
            part = part.strip().lstrip('json').strip()
            if part.startswith('{'):
                raw = part
                break
    return json.loads(raw.strip())


# ── Prompt templates ─────────────────────────────────────────────────────

_FREE = """You are a document analyzer. Identify the document type then analyze it.
Return ONLY valid JSON:
{"document_type":"CV/Resume","overall_score":45,"verdict":"NEEDS WORK",
"summary":"2-3 sentence honest assessment","roast_lines":[
{"type":"fire","text":"critical observation"},
{"type":"amber","text":"warning or suggestion"},
{"type":"green","text":"something good"}],
"top_fixes":["most important fix"],"estimated_interview_chance":"Low"}
LANG_RULE
DOCUMENT TEXT:
CVTEXT"""

_PRO = """You are a brutally honest document analyst like Gordon Ramsay reviewing food.
Return ONLY valid JSON:
{"document_type":"CV/Resume","overall_score":45,"verdict":"NEEDS WORK",
"summary":"2-3 sentence brutal assessment",
"sections":{"structure":{"score":70,"feedback":"..."},"content_quality":{"score":30,"feedback":"..."},
"language_style":{"score":50,"feedback":"..."},"completeness":{"score":60,"feedback":"..."},
"formatting":{"score":40,"feedback":"..."},"overall_impact":{"score":55,"feedback":"..."}},
"roast_lines":[{"type":"fire","text":"..."},{"type":"fire","text":"..."},
{"type":"amber","text":"..."},{"type":"amber","text":"..."},
{"type":"green","text":"..."},{"type":"green","text":"..."},
{"type":"amber","text":"..."},{"type":"fire","text":"..."}],
"top_fixes":["fix 1","fix 2","fix 3"],"ats_score":40,
"ats_issues":["issue 1","issue 2"],"language_quality":50,
"banned_phrases":["weak phrase"],"strengths":["strength 1","strength 2"],
"estimated_interview_chance":"Low"}
LANG_RULE
DOCUMENT TEXT:
CVTEXT"""

_VIP = """You are an ultra-analytical document expert. Give the most detailed analysis possible.
Return ONLY valid JSON:
{"document_type":"CV/Resume","overall_score":45,"verdict":"NEEDS WORK",
"summary":"3-4 sentence deep assessment with specific examples",
"sections":{"structure":{"score":70,"feedback":"very specific detailed feedback"},
"content_quality":{"score":30,"feedback":"very specific detailed feedback"},
"language_style":{"score":50,"feedback":"very specific feedback with examples"},
"completeness":{"score":60,"feedback":"very specific detailed feedback"},
"formatting":{"score":55,"feedback":"very specific detailed feedback"},
"overall_impact":{"score":40,"feedback":"very specific detailed feedback"}},
"roast_lines":[{"type":"fire","text":"brutal funny observation"},
{"type":"fire","text":"brutal observation with specific example"},
{"type":"fire","text":"another brutal observation"},
{"type":"amber","text":"detailed warning with specific example"},
{"type":"amber","text":"detailed warning"},{"type":"amber","text":"another warning"},
{"type":"green","text":"specific positive with example"},
{"type":"green","text":"another specific positive"},
{"type":"amber","text":"improvement with solution"},
{"type":"fire","text":"final devastating but true observation"}],
"top_fixes":["detailed fix 1","detailed fix 2","fix 3","fix 4","fix 5"],
"rewrite_suggestions":[{"original":"weak phrase","improved":"stronger version"},
{"original":"another weak phrase","improved":"stronger version"},
{"original":"third weak phrase","improved":"stronger version"}],
"ats_score":40,"ats_issues":["issue 1","issue 2","issue 3"],
"language_quality":50,"banned_phrases":["cliche 1","cliche 2"],
"strengths":["strength 1","strength 2","strength 3"],
"career_path_advice":"Detailed career advice based on this document",
"salary_estimate":"Salary estimate based on experience level",
"linkedin_tips":["specific tip 1","tip 2","tip 3"],
"interview_questions":["question 1","question 2","question 3","question 4","question 5"],
"industry_benchmark":"How this compares to similar CVs in this field",
"estimated_interview_chance":"Low"}
LANG_RULE
DOCUMENT TEXT:
CVTEXT"""


# ═══════════════════════════════════════════════════════════════════════════
#  CV ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════

def analyze_cv(cv_text: str, job_description: str = None,
               plan: str = 'free', language: str = None) -> dict:
    start     = time.time()
    lang_rule = _lang_rule(language)

    if plan == 'vip':
        template, max_tokens, text_limit = _VIP, 4000, 8000
    elif plan == 'pro':
        template, max_tokens, text_limit = _PRO, 2500, 6000
    else:
        template, max_tokens, text_limit = _FREE, 1200, 3000

    prompt = template.replace('LANG_RULE', lang_rule).replace('CVTEXT', cv_text[:text_limit])
    if job_description:
        prompt += f'\n\nJob Description to match against:\n{job_description[:1000]}'

    try:
        result = _call_groq(prompt, max_tokens)
        result['processing_time'] = round(time.time() - start, 2)
        result['plan_used']       = plan
        return result
    except json.JSONDecodeError:
        raise ValueError('AI returned an invalid response. Please try again.')
    except Exception as e:
        raise ValueError(f'AI error: {e}')


# ═══════════════════════════════════════════════════════════════════════════
#  CV COMPARISON
# ═══════════════════════════════════════════════════════════════════════════

def compare_cvs(text_a: str, text_b: str,
                name_a: str = 'Version A', name_b: str = 'Version B',
                language: str = None) -> dict:
    lang_rule = _lang_rule(language)
    prompt = f"""Compare two CV versions and return a JSON comparison report.
Return ONLY valid JSON:
{{"winner":"{name_a} or {name_b} or Tie","score_a":65,"score_b":72,
"verdict_a":"GETTING THERE","verdict_b":"PRETTY SOLID",
"summary":"2-3 sentence overall comparison",
"sections":[
{{"name":"Structure","score_a":60,"score_b":75,"winner":"{name_b}","feedback":"specific comparison"}},
{{"name":"Content Quality","score_a":70,"score_b":65,"winner":"{name_a}","feedback":"specific comparison"}},
{{"name":"Language & Style","score_a":55,"score_b":80,"winner":"{name_b}","feedback":"specific comparison"}},
{{"name":"Completeness","score_a":65,"score_b":70,"winner":"{name_b}","feedback":"what changed"}},
{{"name":"ATS Friendliness","score_a":50,"score_b":75,"winner":"{name_b}","feedback":"keywords comparison"}}],
"improvements_in_b":["what got better"],"regressions_in_b":["what got worse if anything"],
"best_of_both":["element from A to keep","element from B that is great"],
"next_steps":["action item 1","action item 2","action item 3"]}}

{lang_rule}
--- {name_a} ---
{text_a[:4000]}
--- {name_b} ---
{text_b[:4000]}"""

    try:
        start  = time.time()
        result = _call_groq(prompt, 2000)
        result['processing_time'] = round(time.time() - start, 2)
        result['name_a'] = name_a
        result['name_b'] = name_b
        return result
    except json.JSONDecodeError:
        raise ValueError('AI returned an invalid comparison response. Please try again.')
    except Exception as e:
        raise ValueError(f'AI error during comparison: {e}')


# ═══════════════════════════════════════════════════════════════════════════
#  ATS OPTIMIZER
# ═══════════════════════════════════════════════════════════════════════════

def optimize_ats(cv_text: str, job_description: str, language: str = None) -> dict:
    """Optimize a CV specifically for ATS matching against a job description."""
    lang_rule = _lang_rule(language)
    prompt = f"""You are an ATS (Applicant Tracking System) optimization expert.
Analyze the CV against the job description and return a detailed optimization plan.

Return ONLY valid JSON:
{{"original_ats_score":45,"optimized_ats_score":82,
"keywords_found":["keyword from JD already in CV"],
"keywords_missing":["important keyword from JD missing in CV"],
"optimized_summary":"A rewritten professional summary packed with JD keywords",
"optimized_skills":["skill 1 from JD","skill 2","skill 3","skill 4","skill 5"],
"optimized_bullets":[
{{"original":"current bullet from CV","improved":"improved bullet with JD keywords"}},
{{"original":"another bullet","improved":"improved version"}}],
"sections_to_add":["section missing that JD requires"],
"formatting_tips":["ATS formatting tip 1","tip 2"],
"overall_tips":["key tip 1","key tip 2","key tip 3"]}}

{lang_rule}

JOB DESCRIPTION:
{job_description[:2000]}

CV TEXT:
{cv_text[:5000]}"""

    try:
        start  = time.time()
        result = _call_groq(prompt, 2500)
        result['processing_time'] = round(time.time() - start, 2)
        return result
    except json.JSONDecodeError:
        raise ValueError('AI returned an invalid response. Please try again.')
    except Exception as e:
        raise ValueError(f'AI error: {e}')


# ═══════════════════════════════════════════════════════════════════════════
#  CV BUILDER
# ═══════════════════════════════════════════════════════════════════════════

def build_cv(data: dict, language: str = None) -> dict:
    """
    Build a professional CV from structured user input.
    data keys: name, email, phone, location, title, summary_hint,
               experience (list), education (list), skills (list), projects (list)
    """
    lang_rule = _lang_rule(language)

    exp_text = '\n'.join([
        f"- {e.get('role','')} at {e.get('company','')} ({e.get('dates','')}):\n  {e.get('description','')}"
        for e in data.get('experience', [])
    ])
    edu_text = '\n'.join([
        f"- {e.get('degree','')} at {e.get('school','')} ({e.get('dates','')})"
        for e in data.get('education', [])
    ])
    proj_text = '\n'.join([
        f"- {p.get('name','')}: {p.get('description','')} (Tech: {p.get('tech','')})"
        for p in data.get('projects', [])
    ])
    skills_text = ', '.join(data.get('skills', []))

    prompt = f"""You are a professional CV writer. Build a polished, ATS-friendly CV from this information.

Return ONLY valid JSON:
{{"contact":{{"name":"{data.get('name','')}","email":"{data.get('email','')}",
"phone":"{data.get('phone','')}","location":"{data.get('location','')}"}},
"title":"{data.get('title','')}",
"summary":"A compelling 3-4 sentence professional summary. Reference the person title and key skills.",
"experience":[
{{"company":"","role":"","dates":"",
"bullets":["achievement bullet using numbers and action verbs","another achievement bullet","third bullet"]}}],
"education":[{{"school":"","degree":"","dates":"","gpa":""}}],
"skills":{{"technical":["skill 1","skill 2","skill 3"],"soft":["skill 1","skill 2"]}},
"projects":[{{"name":"","description":"one strong sentence","tech":["tech 1","tech 2"],"link":""}}],
"certifications":[],"languages":[]}}

Rules:
- Use strong action verbs (Led, Built, Increased, Reduced, Delivered)
- Add quantified achievements where possible (%, $, time saved)
- Make it ATS-friendly with relevant keywords
- Keep each bullet under 2 lines

{lang_rule}

PERSON INFO:
Name: {data.get('name','')}
Target Title: {data.get('title','')}
Summary hint: {data.get('summary_hint','')}

EXPERIENCE:
{exp_text}

EDUCATION:
{edu_text}

SKILLS: {skills_text}

PROJECTS:
{proj_text}"""

    try:
        start  = time.time()
        result = _call_groq(prompt, 3000)
        result['processing_time'] = round(time.time() - start, 2)
        return result
    except json.JSONDecodeError:
        raise ValueError('AI returned an invalid response. Please try again.')
    except Exception as e:
        raise ValueError(f'AI error: {e}')
