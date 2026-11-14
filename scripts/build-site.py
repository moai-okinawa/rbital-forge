#!/usr/bin/env python3
"""Render the fictional company brief into a dependency-free static page."""
import argparse
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    'manufacturing': '製造・研究', 'operations': '建設・運用',
    'logistics': '輸送・循環', 'lunar': '月面開発',
}


def escape(value):
    return html.escape(str(value), quote=True)


def paragraphs(values, class_name=''):
    attribute = f' class="{class_name}"' if class_name else ''
    return '\n'.join(f'<p{attribute}>{escape(value)}</p>' for value in values)


def items(values):
    return '\n'.join(f'<li>{escape(value)}</li>' for value in values)


def business_card(business):
    name, title = escape(business['name']), escape(business['title'])
    return f'''<article class="business" id="{escape(business['id'])}" data-category="{escape(business['category'])}">
  <div class="business-heading"><span class="business-number">{business['number']:02d}</span><span class="category-label">{CATEGORIES[business['category']]}</span></div>
  <h3>{name}</h3><p class="business-title">{title}</p>
  <p class="business-intro">{escape(business['paragraphs'][0])}</p>
  <details><summary aria-label="事業の詳細：{name}"><span>事業の詳細</span><span class="disclosure-icon" aria-hidden="true">＋</span></summary>
    <div class="detail-body">{paragraphs(business['paragraphs'][1:])}
      <h4>提供サービス</h4><ul class="service-list">{items(business['services'])}</ul>
      <dl class="detail-facts"><div><dt>主な顧客</dt><dd>{escape(business['customers'])}</dd></div><div><dt>収益源</dt><dd>{escape(business['revenue'])}</dd></div></dl>
    </div>
  </details>
</article>'''


def achievement_card(achievement):
    name = escape(achievement['name'])
    return f'''<article class="achievement" id="{escape(achievement['id'])}">
  <div class="achievement-year">{escape(achievement['year'])}<span aria-hidden="true">↗</span></div>
  <p class="eyebrow">{name}</p><h3>{escape(achievement['title'])}</h3>
  {paragraphs(achievement['paragraphs'], 'achievement-description')}
  <details><summary aria-label="成果を見る：{name}"><span>成果を見る</span><span class="disclosure-icon" aria-hidden="true">＋</span></summary><div class="detail-body"><ul class="outcome-list">{items(achievement['outcomes'])}</ul></div></details>
  <blockquote>「{escape(achievement['quote'])}」</blockquote>
</article>'''


def render():
    data = json.loads((ROOT / 'content/company.json').read_text())
    facility = data['facility']
    facts = '\n'.join(f'<div><dt>{escape(fact["label"])}</dt><dd>{escape(fact["value"])}</dd></div>' for fact in data['facts'])
    filters = f'<button type="button" data-filter="all" aria-pressed="true">すべて <span>{len(data["businesses"])}</span></button>'
    for category, label in CATEGORIES.items():
        count = sum(business['category'] == category for business in data['businesses'])
        filters += f'<button type="button" data-filter="{category}" aria-pressed="false">{label} <span>{count}</span></button>'
    replacements = {
        'NAME': escape(data['name']), 'JAPANESE_NAME': escape(data['japanese_name']),
        'TAGLINE': escape(data['tagline']),
        'HERO_HEADLINE': escape(data['tagline']).replace('、', '、<br>', 1),
        'PHILOSOPHY': escape(data['philosophy']),
        'FICTION_NOTICE': escape(data['fiction_notice']),
        'REFERENCE_NOTE': escape(data['reference_note']),
        'DESCRIPTION': paragraphs(data['description']),
        'FACTS': facts, 'FILTERS': filters,
        'BUSINESSES': '\n'.join(business_card(business) for business in data['businesses']),
        'FACILITY_NAME': escape(facility['name']), 'FACILITY_TITLE': escape(facility['title']),
        'FACILITY_DESCRIPTION': paragraphs(facility['paragraphs']),
        'FACILITY_EQUIPMENT': items(facility['equipment']), 'FACILITY_ROLE': escape(facility['role']),
        'ACHIEVEMENTS': '\n'.join(achievement_card(achievement) for achievement in data['achievements']),
        'STRENGTHS': paragraphs(data['strengths']),
    }
    page = (ROOT / 'templates/index.html').read_text()
    for key, value in replacements.items():
        placeholder = '{{' + key + '}}'
        if placeholder not in page:
            raise ValueError(f'Unused content placeholder: {key}')
        page = page.replace(placeholder, value)
    if '{{' in page:
        raise ValueError('Unresolved template placeholder')
    return page


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if the committed page is out of date.')
    args = parser.parse_args()
    output = ROOT / 'dist/index.html'
    rendered = render()
    if args.check:
        if output.read_text() != rendered:
            parser.exit(1, 'dist/index.html is out of date. Run python3 scripts/build-site.py.\n')
        print('PASS: generated page matches company content and template')
    else:
        output.write_text(rendered)
        print('Generated dist/index.html')
