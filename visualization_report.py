#!/usr/bin/env python3
"""
Create ASCII visualizations for key findings
"""

import pandas as pd
import numpy as np

print("=" * 80)
print("KEY FINDINGS - VISUAL SUMMARY")
print("=" * 80)
print()

products = pd.read_csv('products.csv')
marketing = pd.read_csv('marketing.csv')
reviews = pd.read_csv('reviews.csv')

# Convert dates
products['launch_date'] = pd.to_datetime(products['launch_date'])
marketing['start_date'] = pd.to_datetime(marketing['start_date'])
marketing['end_date'] = pd.to_datetime(marketing['end_date'])
reviews['date'] = pd.to_datetime(reviews['date'])

print("1. RATING DISTRIBUTION")
print("-" * 80)
rating_bins = [0, 1.5, 2.5, 3.5, 4.5, 6]
rating_labels = ['1 ⭐', '2 ⭐⭐', '3 ⭐⭐⭐', '4 ⭐⭐⭐⭐', '5 ⭐⭐⭐⭐⭐']
reviews['rating_category'] = pd.cut(reviews['rating'], bins=rating_bins, labels=rating_labels, include_lowest=True)
rating_dist = reviews['rating_category'].value_counts().sort_index()

max_count = rating_dist.max()
for category, count in rating_dist.items():
    bar_length = int((count / max_count) * 50)
    bar = '█' * bar_length
    pct = (count / len(reviews)) * 100
    print(f"{category}: {bar} {count:,} ({pct:.1f}%)")

print("\n2. SENTIMENT BREAKDOWN")
print("-" * 80)
sentiment_dist = reviews['sentiment'].value_counts()
total = len(reviews)
for sentiment, count in sentiment_dist.items():
    pct = (count / total) * 100
    bar_length = int(pct / 2)
    bar = '█' * bar_length
    emoji = '😞' if sentiment == 'Negative' else ('😊' if sentiment == 'Positive' else '😐')
    print(f"{emoji} {sentiment:10s}: {bar} {count:,} ({pct:.1f}%)")

print("\n3. TOP 10 PRODUCTS BY REVIEW VOLUME")
print("-" * 80)
product_counts = reviews.groupby('product_id').size().sort_values(ascending=False).head(10)
product_info = products.set_index('product_id')[['product_name', 'brand']]

for pid, count in product_counts.items():
    if pid in product_info.index:
        name = product_info.loc[pid, 'product_name']
        brand = product_info.loc[pid, 'brand']
        bar_length = int((count / product_counts.max()) * 40)
        bar = '█' * bar_length
        avg_rating = reviews[reviews['product_id'] == pid]['rating'].mean()
        stars = '⭐' * int(avg_rating)
        print(f"{pid}: {bar} {count} reviews - {avg_rating:.2f} {stars}")
        print(f"       {brand} - {name[:50]}")

print("\n4. MARKETING SPEND BY CHANNEL")
print("-" * 80)
channel_spend = marketing.groupby('channel')['spend_idr'].sum().sort_values(ascending=False)
max_spend = channel_spend.max()

for channel, spend in channel_spend.items():
    bar_length = int((spend / max_spend) * 40)
    bar = '█' * bar_length
    spend_b = spend / 1e9
    pct = (spend / marketing['spend_idr'].sum()) * 100
    print(f"{channel:15s}: {bar} IDR {spend_b:.2f}B ({pct:.1f}%)")

avg_engagement = marketing.groupby('channel')['engagement_rate'].mean().sort_values(ascending=False)
print("\nAverage Engagement Rate by Channel:")
for channel, engagement in avg_engagement.items():
    bar_length = int((engagement) * 50)
    bar = '█' * bar_length
    print(f"{channel:15s}: {bar} {engagement:.1%}")

print("\n5. REVIEW TIMELINE (Reviews per Year)")
print("-" * 80)
reviews['year'] = reviews['date'].dt.year
yearly_reviews = reviews.groupby('year').size()

for year, count in yearly_reviews.items():
    bar_length = int((count / yearly_reviews.max()) * 50)
    bar = '█' * bar_length
    marker = ' ⚠️ FUTURE!' if year > 2025 else ''
    print(f"{year}: {bar} {count:,} reviews{marker}")

print("\n6. PLATFORM DISTRIBUTION (Suspiciously Uniform!)")
print("-" * 80)
platform_dist = reviews['platform'].value_counts()
expected = len(reviews) / len(platform_dist)

for platform, count in platform_dist.items():
    bar_length = int((count / platform_dist.max()) * 50)
    bar = '█' * bar_length
    deviation = ((count - expected) / expected) * 100
    print(f"{platform:15s}: {bar} {count:,} (expected {expected:.0f}, {deviation:+.2f}% deviation)")

print("\n7. MOST COMMON REVIEW COMMENTS")
print("-" * 80)
from collections import Counter
comment_freq = Counter(reviews['comment'])

for i, (comment, count) in enumerate(comment_freq.most_common(8), 1):
    pct = (count / len(reviews)) * 100
    bar_length = int(pct)
    bar = '█' * bar_length

    # Get sentiment distribution for this comment
    comment_reviews = reviews[reviews['comment'] == comment]
    sentiment_counts = comment_reviews['sentiment'].value_counts()

    print(f"\n{i}. '{comment}'")
    print(f"   Frequency: {bar} {count:,} times ({pct:.1f}%)")
    print(f"   Sentiments: Pos:{sentiment_counts.get('Positive', 0)} / Neu:{sentiment_counts.get('Neutral', 0)} / Neg:{sentiment_counts.get('Negative', 0)}")
    print(f"   Rating range: {comment_reviews['rating'].min():.1f} - {comment_reviews['rating'].max():.1f}")

print("\n8. BRAND PERFORMANCE COMPARISON")
print("-" * 80)
brand_reviews = reviews.merge(products[['product_id', 'brand']], on='product_id')
brand_stats = brand_reviews.groupby('brand').agg({
    'rating': ['mean', 'count']
})
brand_stats.columns = ['avg_rating', 'review_count']
brand_stats = brand_stats.sort_values('avg_rating', ascending=False)

for brand, row in brand_stats.iterrows():
    rating = row['avg_rating']
    count = row['review_count']
    bar_length = int((rating / 5) * 30)
    bar = '█' * bar_length
    print(f"{brand:25s}: {bar} {rating:.2f}/5.0 ({count:,} reviews)")

print("\n9. DATA QUALITY SCORE CARD")
print("-" * 80)

def print_score(category, score, max_score, issues):
    pct = (score / max_score) * 100
    if pct >= 80:
        grade = "✅ PASS"
    elif pct >= 50:
        grade = "⚠️  WARN"
    else:
        grade = "❌ FAIL"

    bar_length = int(pct / 2)
    bar = '█' * bar_length
    empty = '░' * (50 - bar_length)
    print(f"{category:30s}: {bar}{empty} {pct:.0f}% {grade}")
    if issues:
        print(f"{'':32s}  └─ {issues}")

# Calculate scores
total_reviews = len(reviews)
future_reviews = len(reviews[reviews['date'] > pd.Timestamp('2025-11-03')])
pre_launch_reviews = len(reviews.merge(products[['product_id', 'launch_date']], on='product_id')[
    reviews.merge(products[['product_id', 'launch_date']], on='product_id')['date'] <
    reviews.merge(products[['product_id', 'launch_date']], on='product_id')['launch_date']
])
mismatched_sentiment = 992
unique_comments = 8

temporal_score = max(0, 100 - (future_reviews + pre_launch_reviews) / total_reviews * 100)
sentiment_score = max(0, 100 - (mismatched_sentiment / total_reviews * 100 * 10))
uniqueness_score = min(100, (unique_comments / total_reviews * 100 * 1000))
distribution_score = 20  # Artificially uniform

print()
print_score("Temporal Integrity", temporal_score, 100, f"{future_reviews + pre_launch_reviews} impossible dates")
print_score("Sentiment Accuracy", sentiment_score, 100, f"{mismatched_sentiment} mismatched labels")
print_score("Content Uniqueness", uniqueness_score, 100, f"Only {unique_comments} unique comments")
print_score("Distribution Naturalness", distribution_score, 100, "Too uniform, suspicious")

overall_score = (temporal_score + sentiment_score + uniqueness_score + distribution_score) / 4
print("\n" + "=" * 80)
print_score("OVERALL DATA QUALITY", overall_score, 100, "")
print("=" * 80)

if overall_score < 50:
    print("\n🚨 VERDICT: DATA QUALITY CRITICAL - LIKELY SYNTHETIC/TEST DATA")
else:
    print("\n✅ VERDICT: DATA QUALITY ACCEPTABLE")

print("\n10. TOP ANOMALIES SUMMARY")
print("-" * 80)
print(f"🔴 Critical Issues Found: 10")
print(f"   1. Future-dated reviews: {future_reviews}")
print(f"   2. Pre-launch reviews: {pre_launch_reviews}")
print(f"   3. Sentiment mismatches: {mismatched_sentiment}")
print(f"   4. Comment uniqueness: {unique_comments}/{total_reviews} (0.08%)")
print(f"   5. Sequential IDs: 100% sequential (no gaps)")
print(f"   6. Platform distribution: < 2% deviation (too perfect)")
print(f"   7. Product review counts: Std = 21 (too uniform)")
print(f"   8. Average ratings: 2.91-3.08 range (too narrow)")
print(f"   9. Marketing ROI: Negative correlation (-0.21)")
print(f"  10. Sales.csv: 100MB file in Git LFS (not analyzed)")

print("\n" + "=" * 80)
print("CONCLUSION: This is SYNTHETIC/SIMULATED data with intentional anomalies")
print("Perfect for testing, training, and demonstrating data quality issues!")
print("=" * 80)
