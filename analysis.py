#!/usr/bin/env python3
"""
Comprehensive Data Analysis Script for CSV files
Analyzes products, marketing, and reviews data
"""

import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("COMPREHENSIVE DATA ANALYSIS REPORT")
print("=" * 80)
print()

# Load all datasets
print("Loading datasets...")
products = pd.read_csv('products.csv')
marketing = pd.read_csv('marketing.csv')
reviews = pd.read_csv('reviews.csv')

print(f"✓ Products: {len(products)} records")
print(f"✓ Marketing: {len(marketing)} records")
print(f"✓ Reviews: {len(reviews)} records")
print()

# Convert date columns
products['launch_date'] = pd.to_datetime(products['launch_date'])
marketing['start_date'] = pd.to_datetime(marketing['start_date'])
marketing['end_date'] = pd.to_datetime(marketing['end_date'])
reviews['date'] = pd.to_datetime(reviews['date'])

TODAY = datetime(2025, 11, 3)  # Current date from environment

print("=" * 80)
print("1. DATA QUALITY ISSUES")
print("=" * 80)
print()

# Check for future dates
print("🔍 TEMPORAL ANOMALIES (Future Dates):")
print("-" * 80)

future_marketing = marketing[marketing['start_date'] > TODAY]
print(f"\n📅 Marketing campaigns starting in the FUTURE: {len(future_marketing)}")
if len(future_marketing) > 0:
    for _, row in future_marketing.iterrows():
        print(f"   - {row['campaign_id']}: {row['product_id']} ({row['start_date'].date()} to {row['end_date'].date()})")

future_reviews = reviews[reviews['date'] > TODAY]
print(f"\n📝 Reviews from the FUTURE: {len(future_reviews)}")
if len(future_reviews) > 0:
    print("   Sample future reviews:")
    for _, row in future_reviews.head(10).iterrows():
        print(f"   - {row['review_id']}: {row['product_id']} on {row['date'].date()}")

# Check for reviews before product launch
print("\n🚨 Reviews BEFORE Product Launch:")
print("-" * 80)
merged = reviews.merge(products[['product_id', 'launch_date']], on='product_id', how='left')
invalid_reviews = merged[merged['date'] < merged['launch_date']]
print(f"Found {len(invalid_reviews)} reviews before product launch date!")
if len(invalid_reviews) > 0:
    for _, row in invalid_reviews.head(10).iterrows():
        print(f"   - {row['review_id']}: {row['product_id']} reviewed on {row['date'].date()}, launched on {row['launch_date'].date()}")

# Check for marketing campaigns before product launch
print("\n🚨 Marketing Campaigns BEFORE Product Launch:")
print("-" * 80)
mkt_merged = marketing.merge(products[['product_id', 'launch_date']], on='product_id', how='left')
invalid_campaigns = mkt_merged[mkt_merged['start_date'] < mkt_merged['launch_date']]
print(f"Found {len(invalid_campaigns)} campaigns before product launch!")
if len(invalid_campaigns) > 0:
    for _, row in invalid_campaigns.head(10).iterrows():
        print(f"   - {row['campaign_id']}: {row['product_id']} campaign on {row['start_date'].date()}, product launched on {row['launch_date'].date()}")

print("\n🔍 SENTIMENT vs RATING vs COMMENT MISMATCHES:")
print("-" * 80)

# Analyze sentiment-rating alignment
def get_expected_sentiment(rating):
    if rating >= 4.0:
        return 'Positive'
    elif rating <= 2.5:
        return 'Negative'
    else:
        return 'Neutral'

reviews['expected_sentiment'] = reviews['rating'].apply(get_expected_sentiment)
mismatched = reviews[reviews['sentiment'] != reviews['expected_sentiment']]
print(f"\nSentiment label doesn't match rating: {len(mismatched)} cases ({len(mismatched)/len(reviews)*100:.1f}%)")

# Check for specific problematic cases
print("\nSample contradictions:")
# High rating but negative comment indicators
negative_words = ['bocor', 'kurang', 'tidak', 'kuat untuk saya']
positive_ratings = reviews[reviews['rating'] >= 4.0]
for word in negative_words:
    contradictions = positive_ratings[positive_ratings['comment'].str.contains(word, case=False, na=False)]
    if len(contradictions) > 0:
        sample = contradictions.head(3)
        for _, row in sample.iterrows():
            print(f"   ⚠️  {row['review_id']}: Rating {row['rating']} ({row['sentiment']}) but comment: '{row['comment']}'")

# Low rating but positive comment indicators
positive_words = ['suka banget', 'tahan lama', 'value for money']
negative_ratings = reviews[reviews['rating'] <= 2.0]
for word in positive_words:
    contradictions = negative_ratings[negative_ratings['comment'].str.contains(word, case=False, na=False)]
    if len(contradictions) > 0:
        sample = contradictions.head(3)
        for _, row in sample.iterrows():
            print(f"   ⚠️  {row['review_id']}: Rating {row['rating']} ({row['sentiment']}) but comment: '{row['comment']}'")

print("\n🔍 DUPLICATE & MISSING DATA:")
print("-" * 80)
print(f"Duplicate product IDs: {products['product_id'].duplicated().sum()}")
print(f"Duplicate campaign IDs: {marketing['campaign_id'].duplicated().sum()}")
print(f"Duplicate review IDs: {reviews['review_id'].duplicated().sum()}")
print(f"Reviews with missing comments: {reviews['comment'].isna().sum()}")
print(f"Reviews with missing ratings: {reviews['rating'].isna().sum()}")

# Check for orphaned records
print("\n🔗 DATA INTEGRITY (Foreign Keys):")
print("-" * 80)
valid_products = set(products['product_id'])
invalid_marketing = marketing[~marketing['product_id'].isin(valid_products)]
invalid_reviews = reviews[~reviews['product_id'].isin(valid_products)]
print(f"Marketing campaigns for non-existent products: {len(invalid_marketing)}")
print(f"Reviews for non-existent products: {len(invalid_reviews)}")

print("\n" + "=" * 80)
print("2. STATISTICAL ANALYSIS")
print("=" * 80)
print()

print("📊 PRODUCTS OVERVIEW:")
print("-" * 80)
print(f"Total products: {len(products)}")
print(f"Brands: {products['brand'].nunique()}")
print(f"Product types: {products['type'].nunique()}")
print(f"\nTop brands by product count:")
print(products['brand'].value_counts().head())
print(f"\nProduct type distribution:")
print(products['type'].value_counts())
print(f"\nPrice statistics:")
print(products['base_price'].describe())

print("\n📊 MARKETING ANALYSIS:")
print("-" * 80)
print(f"Total campaigns: {len(marketing)}")
marketing['duration'] = (marketing['end_date'] - marketing['start_date']).dt.days
print(f"Campaign duration: {marketing['duration'].mean():.1f} days (avg), {marketing['duration'].min()}-{marketing['duration'].max()} days range")
print(f"Total marketing spend: IDR {marketing['spend_idr'].sum():,.0f}")
print(f"Average spend per campaign: IDR {marketing['spend_idr'].mean():,.0f}")
print(f"\nMarketing channels:")
print(marketing['channel'].value_counts())
print(f"\nEngagement rate statistics:")
print(marketing['engagement_rate'].describe())
print(f"\nTop spending campaigns:")
print(marketing.nlargest(5, 'spend_idr')[['campaign_id', 'product_id', 'spend_idr', 'channel', 'engagement_rate']])

print("\n📊 REVIEWS ANALYSIS:")
print("-" * 80)
print(f"Total reviews: {len(reviews)}")
print(f"Average rating: {reviews['rating'].mean():.2f}")
print(f"Rating distribution:")
print(reviews['rating'].describe())
print(f"\nSentiment distribution:")
print(reviews['sentiment'].value_counts())
print(f"\nPlatform distribution:")
print(reviews['platform'].value_counts())

# Most reviewed products
print(f"\nMost reviewed products:")
most_reviewed = reviews.groupby('product_id').size().sort_values(ascending=False).head(10)
for pid, count in most_reviewed.items():
    pname = products[products['product_id'] == pid]['product_name'].values[0] if len(products[products['product_id'] == pid]) > 0 else 'Unknown'
    avg_rating = reviews[reviews['product_id'] == pid]['rating'].mean()
    print(f"   {pid}: {count} reviews (avg rating: {avg_rating:.2f}) - {pname}")

print("\n" + "=" * 80)
print("3. CROSS-DATASET INSIGHTS")
print("=" * 80)
print()

print("🔗 MARKETING ROI ANALYSIS:")
print("-" * 80)
# Calculate reviews per product during/after campaign period
for _, campaign in marketing.head(10).iterrows():
    pid = campaign['product_id']
    campaign_reviews = reviews[
        (reviews['product_id'] == pid) &
        (reviews['date'] >= campaign['start_date']) &
        (reviews['date'] <= campaign['end_date'] + pd.Timedelta(days=30))
    ]
    if len(campaign_reviews) > 0:
        avg_rating = campaign_reviews['rating'].mean()
        print(f"{campaign['campaign_id']} ({campaign['channel']}): {len(campaign_reviews)} reviews, avg rating {avg_rating:.2f}, engagement {campaign['engagement_rate']:.1%}, spend IDR {campaign['spend_idr']:,.0f}")

print("\n📈 PRODUCT PERFORMANCE:")
print("-" * 80)
product_stats = reviews.groupby('product_id').agg({
    'rating': ['mean', 'count'],
    'sentiment': lambda x: (x == 'Positive').sum() / len(x)
}).round(2)
product_stats.columns = ['avg_rating', 'review_count', 'positive_ratio']
product_stats = product_stats.sort_values('avg_rating', ascending=False)

# Merge with product info
product_performance = products.merge(product_stats, left_on='product_id', right_index=True, how='left')
product_performance = product_performance.sort_values('avg_rating', ascending=False)

print("Top 5 rated products:")
for _, row in product_performance.head(5).iterrows():
    print(f"   {row['product_id']}: {row['product_name']} - {row['avg_rating']:.2f} avg rating ({row['review_count']:.0f} reviews)")

print("\nWorst 5 rated products:")
for _, row in product_performance.tail(5).iterrows():
    if not pd.isna(row['avg_rating']):
        print(f"   {row['product_id']}: {row['product_name']} - {row['avg_rating']:.2f} avg rating ({row['review_count']:.0f} reviews)")

print("\n🎯 BRAND PERFORMANCE:")
print("-" * 80)
brand_reviews = reviews.merge(products[['product_id', 'brand']], on='product_id')
brand_stats = brand_reviews.groupby('brand').agg({
    'rating': ['mean', 'count'],
    'sentiment': lambda x: (x == 'Positive').sum() / len(x) * 100
}).round(2)
brand_stats.columns = ['avg_rating', 'total_reviews', 'positive_pct']
brand_stats = brand_stats.sort_values('avg_rating', ascending=False)
print(brand_stats)

print("\n💰 MARKETING EFFICIENCY:")
print("-" * 80)
# Cost per engagement point
marketing['cost_per_engagement'] = marketing['spend_idr'] / (marketing['engagement_rate'] * 100)
channel_efficiency = marketing.groupby('channel').agg({
    'spend_idr': 'sum',
    'engagement_rate': 'mean',
    'campaign_id': 'count',
    'cost_per_engagement': 'mean'
}).round(2)
channel_efficiency.columns = ['total_spend', 'avg_engagement', 'num_campaigns', 'avg_cost_per_engagement']
channel_efficiency = channel_efficiency.sort_values('avg_engagement', ascending=False)
print(channel_efficiency)

print("\n" + "=" * 80)
print("4. UNIQUE INSIGHTS & PATTERNS")
print("=" * 80)
print()

# Comment frequency analysis
print("🗣️  REVIEW COMMENT PATTERNS:")
print("-" * 80)
comment_freq = Counter(reviews['comment'])
print(f"Unique comments: {len(comment_freq)} out of {len(reviews)} reviews")
print(f"Most repeated comments:")
for comment, count in comment_freq.most_common(10):
    pct = count / len(reviews) * 100
    print(f"   '{comment}' - {count} times ({pct:.1f}%)")

# Suspicious pattern: same comment with different sentiments
print("\n🚩 SAME COMMENT, DIFFERENT SENTIMENTS/RATINGS:")
print("-" * 80)
for comment, count in comment_freq.most_common(5):
    subset = reviews[reviews['comment'] == comment]
    if subset['sentiment'].nunique() > 1 or subset['rating'].std() > 1.0:
        print(f"\nComment: '{comment}'")
        print(f"  Appears {count} times with:")
        print(f"  - Sentiments: {subset['sentiment'].value_counts().to_dict()}")
        print(f"  - Rating range: {subset['rating'].min():.1f} - {subset['rating'].max():.1f}")

# Platform bias
print("\n📱 PLATFORM RATING BIAS:")
print("-" * 80)
platform_bias = reviews.groupby('platform')['rating'].agg(['mean', 'std', 'count']).round(2)
platform_bias = platform_bias.sort_values('mean', ascending=False)
print(platform_bias)

# Temporal patterns
print("\n📅 TEMPORAL PATTERNS:")
print("-" * 80)
reviews['year'] = reviews['date'].dt.year
reviews['month'] = reviews['date'].dt.month
yearly_reviews = reviews.groupby('year').size()
print("Reviews by year:")
print(yearly_reviews)

monthly_avg_rating = reviews.groupby('month')['rating'].mean().round(2)
print("\nAverage rating by month:")
print(monthly_avg_rating)

# Campaign timing analysis
print("\n⏰ CAMPAIGN TIMING:")
print("-" * 80)
marketing['start_month'] = marketing['start_date'].dt.month
marketing['start_year'] = marketing['start_date'].dt.year
campaign_timing = marketing.groupby('start_month').size()
print("Campaigns started by month:")
print(campaign_timing)

print("\n" + "=" * 80)
print("5. SUMMARY OF CRITICAL FINDINGS")
print("=" * 80)
print()

print("🚨 CRITICAL DATA QUALITY ISSUES:")
print("-" * 80)
print(f"1. {len(future_reviews)} reviews are dated in the FUTURE (after Nov 3, 2025)")
print(f"2. {len(future_marketing)} marketing campaigns start in the FUTURE")
print(f"3. {len(invalid_reviews)} reviews exist BEFORE product launch dates")
print(f"4. {len(invalid_campaigns)} marketing campaigns started BEFORE product launch")
print(f"5. {len(mismatched)} reviews ({len(mismatched)/len(reviews)*100:.1f}%) have sentiment labels that don't match ratings")
print(f"6. Only {len(comment_freq)} unique comments for {len(reviews)} reviews - suggesting synthetic/template data")
print(f"7. Same comments appear with contradictory ratings and sentiments")

print("\n💡 KEY BUSINESS INSIGHTS:")
print("-" * 80)
print(f"1. Total marketing spend: IDR {marketing['spend_idr'].sum():,.0f}")
print(f"2. Average product rating: {reviews['rating'].mean():.2f}/5.0")
print(f"3. Best performing channel: {channel_efficiency.index[0]} (engagement: {channel_efficiency.iloc[0]['avg_engagement']:.1%})")
print(f"4. Most reviewed product: {most_reviewed.index[0]} ({most_reviewed.iloc[0]} reviews)")
print(f"5. Review platforms: {reviews['platform'].nunique()} different platforms")

print("\n⚠️  DATA RELIABILITY ASSESSMENT:")
print("-" * 80)
print("VERDICT: This dataset appears to be SYNTHETIC/SIMULATED with multiple quality issues:")
print("  - Future-dated records (impossible in real data)")
print("  - Reviews before product launches (temporal impossibility)")
print("  - Highly repetitive comments (low diversity)")
print("  - Sentiment-rating-comment contradictions (labeling errors)")
print("  - Perfect comment templates reused with different sentiments")
print("\nThis data likely generated for testing/demonstration purposes, not real customer data.")

print("\n" + "=" * 80)
print("END OF ANALYSIS")
print("=" * 80)
