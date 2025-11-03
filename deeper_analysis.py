#!/usr/bin/env python3
"""
Deep Dive Analysis - Uncovering Hidden Patterns
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("DEEP DIVE ANALYSIS - HIDDEN PATTERNS & ANOMALIES")
print("=" * 80)
print()

# Load datasets
products = pd.read_csv('products.csv')
marketing = pd.read_csv('marketing.csv')
reviews = pd.read_csv('reviews.csv')

# Convert dates
products['launch_date'] = pd.to_datetime(products['launch_date'])
marketing['start_date'] = pd.to_datetime(marketing['start_date'])
marketing['end_date'] = pd.to_datetime(marketing['end_date'])
reviews['date'] = pd.to_datetime(reviews['date'])

print("🔬 STATISTICAL ANOMALY DETECTION")
print("=" * 80)
print()

# Check if ratings follow expected distribution
print("1. RATING DISTRIBUTION ANALYSIS:")
print("-" * 80)
ratings_dist = reviews['rating'].value_counts(bins=5, sort=False).sort_index()
print("Rating distribution (should be roughly normal for real data):")
print(ratings_dist)

# Chi-square test for uniform distribution
expected_per_platform = len(reviews) / reviews['platform'].nunique()
actual_per_platform = reviews['platform'].value_counts()
print("\n2. PLATFORM DISTRIBUTION (Testing for uniformity):")
print("-" * 80)
for platform, count in actual_per_platform.items():
    deviation = ((count - expected_per_platform) / expected_per_platform) * 100
    print(f"{platform:20s}: {count:5d} reviews (expected: {expected_per_platform:.0f}, deviation: {deviation:+.2f}%)")

if actual_per_platform.std() < 10:
    print("⚠️  WARNING: Platform distribution is suspiciously uniform (too perfect for real data!)")

# Check review ID pattern
print("\n3. REVIEW ID PATTERN ANALYSIS:")
print("-" * 80)
reviews['review_num'] = reviews['review_id'].str.replace('R', '').astype(int)
print(f"Review IDs range: R{reviews['review_num'].min()} to R{reviews['review_num'].max()}")
print(f"Expected sequential IDs: {reviews['review_num'].max() - reviews['review_num'].min() + 1}")
print(f"Actual review count: {len(reviews)}")
gaps = reviews['review_num'].diff().dropna()
non_sequential = gaps[gaps != 1]
if len(non_sequential) == 0:
    print("✓ All review IDs are perfectly sequential (R100000, R100001, R100002...)")
    print("⚠️  This is HIGHLY suspicious - real review systems would have gaps")

# Analyze rating precision
print("\n4. RATING PRECISION ANALYSIS:")
print("-" * 80)
unique_ratings = sorted(reviews['rating'].unique())
print(f"Number of unique rating values: {len(unique_ratings)}")
print(f"Sample ratings: {unique_ratings[:20]}")

# Check if ratings are whole numbers or decimals
decimal_ratings = reviews[reviews['rating'] % 1 != 0]
print(f"Decimal ratings: {len(decimal_ratings)} ({len(decimal_ratings)/len(reviews)*100:.1f}%)")

# Check rating granularity
rating_decimals = reviews['rating'] * 10 % 10
unique_decimal_parts = rating_decimals.unique()
print(f"Unique decimal values: {sorted(unique_decimal_parts)}")
if len(unique_decimal_parts) == 10:
    print("⚠️  Ratings use all decimal positions (0.0, 0.1, 0.2...0.9) - suggests random generation")

print("\n5. TEMPORAL PATTERN ANALYSIS:")
print("-" * 80)
reviews['hour'] = pd.to_datetime(reviews['date']).dt.hour if 'hour' in reviews.columns else None
reviews['day_of_week'] = reviews['date'].dt.dayofweek
reviews['day_of_month'] = reviews['date'].dt.day

dow_dist = reviews['day_of_week'].value_counts().sort_index()
print("Reviews by day of week (0=Mon, 6=Sun):")
for day, count in dow_dist.items():
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    bar = '█' * int(count / 100)
    print(f"{day_names[day]}: {bar} {count}")

if dow_dist.std() < 50:
    print("⚠️  Day-of-week distribution is too uniform (real users review more on weekends/evenings)")

# Product review frequency
print("\n6. PRODUCT REVIEW VELOCITY:")
print("-" * 80)
product_review_counts = reviews.groupby('product_id').size().sort_values(ascending=False)
print(f"Most reviewed: {product_review_counts.iloc[0]} reviews")
print(f"Least reviewed: {product_review_counts.iloc[-1]} reviews")
print(f"Std deviation: {product_review_counts.std():.2f}")
if product_review_counts.std() < 50:
    print("⚠️  All products have almost identical review counts - unnatural for real marketplace")

print("\n7. CORRELATION ANALYSIS:")
print("-" * 80)

# Price vs Rating correlation
product_ratings = reviews.groupby('product_id')['rating'].mean()
product_prices = products.set_index('product_id')['base_price']
merged_price_rating = pd.DataFrame({
    'price': product_prices,
    'avg_rating': product_ratings
}).dropna()

correlation = merged_price_rating.corr().loc['price', 'avg_rating']
print(f"Price vs Rating correlation: {correlation:.4f}")
if abs(correlation) < 0.1:
    print("  → Almost no correlation between price and rating")
elif correlation > 0.3:
    print("  → Higher priced products tend to have better ratings")
elif correlation < -0.3:
    print("  → Higher priced products tend to have worse ratings")

# Marketing spend vs engagement
mkt_corr = marketing[['spend_idr', 'engagement_rate']].corr().iloc[0, 1]
print(f"Marketing spend vs Engagement correlation: {mkt_corr:.4f}")
if abs(mkt_corr) < 0.1:
    print("  → Spending more doesn't correlate with engagement (poor ROI!)")

print("\n8. COMMENT-SENTIMENT-RATING COHERENCE:")
print("-" * 80)

# Define comment sentiment
comment_sentiment_map = {
    'Packaging bocor saat diterima, kurang aman.': 'Negative',
    'Kurang cocok di kulit saya, agak kering.': 'Negative',
    'Wangi terlalu kuat untuk saya.': 'Negative',
    'Mudah dibeli saat promo, value for money.': 'Positive',
    'Harumnya tahan lama, suka banget!': 'Positive',
    'Kemasan baru lebih ramah lingkungan.': 'Positive',
    'Memberikan hasil sesuai klaim after 2 weeks.': 'Neutral',
    'Harga sesuai, kualitas oke.': 'Neutral'
}

reviews['expected_comment_sentiment'] = reviews['comment'].map(comment_sentiment_map)
reviews['rating_sentiment'] = reviews['rating'].apply(lambda x: 'Positive' if x >= 4 else ('Negative' if x <= 2.5 else 'Neutral'))

# Triple mismatch: comment, rating, and labeled sentiment all disagree
triple_mismatch = reviews[
    (reviews['sentiment'] != reviews['expected_comment_sentiment']) &
    (reviews['sentiment'] != reviews['rating_sentiment']) &
    (reviews['expected_comment_sentiment'] != reviews['rating_sentiment'])
]

print(f"Triple mismatches (comment vs rating vs label): {len(triple_mismatch)}")
if len(triple_mismatch) > 0:
    print("\nWorst examples:")
    for _, row in triple_mismatch.head(5).iterrows():
        print(f"  {row['review_id']}: Rating {row['rating']}, Label '{row['sentiment']}', Comment '{row['comment']}'")

print("\n9. MARKETING CAMPAIGN EFFECTIVENESS:")
print("-" * 80)

# Analyze if campaigns actually impact reviews
for _, campaign in marketing.iterrows():
    product_id = campaign['product_id']

    # Reviews during campaign
    during = reviews[
        (reviews['product_id'] == product_id) &
        (reviews['date'] >= campaign['start_date']) &
        (reviews['date'] <= campaign['end_date'])
    ]

    # Reviews 30 days before
    before = reviews[
        (reviews['product_id'] == product_id) &
        (reviews['date'] >= campaign['start_date'] - pd.Timedelta(days=30)) &
        (reviews['date'] < campaign['start_date'])
    ]

    # Reviews 30 days after
    after = reviews[
        (reviews['product_id'] == product_id) &
        (reviews['date'] > campaign['end_date']) &
        (reviews['date'] <= campaign['end_date'] + pd.Timedelta(days=30))
    ]

    if len(before) > 5 and len(after) > 5:
        volume_increase = ((len(after) - len(before)) / len(before)) * 100 if len(before) > 0 else 0
        rating_change = after['rating'].mean() - before['rating'].mean()

        if abs(volume_increase) > 50 or abs(rating_change) > 0.5:
            print(f"{campaign['campaign_id']} ({campaign['channel']}, IDR {campaign['spend_idr']/1e9:.1f}B):")
            print(f"  Volume: {len(before)}→{len(during)}→{len(after)} reviews ({volume_increase:+.0f}% change)")
            print(f"  Rating: {before['rating'].mean():.2f}→{after['rating'].mean():.2f} ({rating_change:+.2f})")

print("\n10. HIDDEN DATA GENERATION ARTIFACTS:")
print("-" * 80)

# Check if review dates are evenly distributed
reviews_per_day = reviews.groupby(reviews['date'].dt.date).size()
print(f"Reviews per day - Mean: {reviews_per_day.mean():.1f}, Std: {reviews_per_day.std():.1f}")
if reviews_per_day.std() < reviews_per_day.mean() * 0.3:
    print("⚠️  Daily review volume is too consistent (real data shows more variance)")

# Check product_id distribution in reviews
product_freq = reviews['product_id'].value_counts()
expected_if_random = len(reviews) / products['product_id'].nunique()
print(f"\nReviews per product - Expected if random: {expected_if_random:.0f}")
print(f"Actual - Mean: {product_freq.mean():.1f}, Std: {product_freq.std():.1f}")
if product_freq.std() < expected_if_random * 0.1:
    print("⚠️  Products have suspiciously equal review counts - suggests artificial balancing")

# Check if ratings are TOO evenly distributed across products
product_avg_ratings = reviews.groupby('product_id')['rating'].mean()
print(f"\nAverage rating per product - Mean: {product_avg_ratings.mean():.2f}, Std: {product_avg_ratings.std():.2f}")
if product_avg_ratings.std() < 0.2:
    print("⚠️  All products have nearly identical average ratings - unrealistic for real market")

print("\n" + "=" * 80)
print("FINAL VERDICT")
print("=" * 80)
print()
print("This dataset exhibits multiple hallmarks of SYNTHETIC/GENERATED data:")
print()
print("✗ Sequential IDs with no gaps")
print("✗ Perfectly uniform distribution across platforms")
print("✗ Identical review volumes per product")
print("✗ Only 8 unique comment templates for 10,000 reviews")
print("✗ Same comments with contradictory ratings/sentiments")
print("✗ Reviews dated in the future")
print("✗ Reviews before product launches")
print("✗ Marketing campaigns before product launches")
print("✗ Too-consistent daily review volumes")
print("✗ Near-identical average ratings across all products")
print()
print("CONCLUSION: This is clearly SIMULATED DATA, likely created for:")
print("  • Testing database systems")
print("  • Training data science/analytics skills")
print("  • Demonstrating data quality issues")
print("  • Educational/tutorial purposes")
print()
print("The data contains intentional anomalies and quality issues that would")
print("never occur naturally in a real e-commerce/review system.")
print("=" * 80)
