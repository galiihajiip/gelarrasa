#!/usr/bin/env python3
"""
Data Cleaning Pipeline for Competition Submission
Systematically cleans the synthetic dataset while documenting all decisions
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("DATA CLEANING PIPELINE FOR COMPETITION")
print("=" * 80)
print()

# Load original data
print("Loading original datasets...")
products = pd.read_csv('products.csv')
marketing = pd.read_csv('marketing.csv')
reviews = pd.read_csv('reviews.csv')

# Convert dates
products['launch_date'] = pd.to_datetime(products['launch_date'])
marketing['start_date'] = pd.to_datetime(marketing['start_date'])
marketing['end_date'] = pd.to_datetime(marketing['end_date'])
reviews['date'] = pd.to_datetime(reviews['date'])

TODAY = datetime(2025, 11, 3)

print(f"Original sizes:")
print(f"  Products: {len(products)}")
print(f"  Marketing: {len(marketing)}")
print(f"  Reviews: {len(reviews)}")
print()

# Track cleaning operations
cleaning_log = []

print("=" * 80)
print("CLEANING OPERATIONS")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Temporal Cleaning
# ============================================================================
print("STEP 1: Temporal Integrity Cleaning")
print("-" * 80)

# Remove future-dated reviews
future_reviews = reviews[reviews['date'] > TODAY]
print(f"Removing {len(future_reviews)} future-dated reviews (after {TODAY.date()})")
reviews_clean = reviews[reviews['date'] <= TODAY].copy()
cleaning_log.append(f"Removed {len(future_reviews)} future-dated reviews")

# Remove reviews before product launch
reviews_with_launch = reviews_clean.merge(
    products[['product_id', 'launch_date']],
    on='product_id',
    how='left'
)
pre_launch = reviews_with_launch[reviews_with_launch['date'] < reviews_with_launch['launch_date']]
print(f"Removing {len(pre_launch)} reviews before product launch dates")
reviews_clean = reviews_with_launch[
    reviews_with_launch['date'] >= reviews_with_launch['launch_date']
].drop('launch_date', axis=1).copy()
cleaning_log.append(f"Removed {len(pre_launch)} pre-launch reviews")

# Remove marketing campaigns before product launch
marketing_with_launch = marketing.merge(
    products[['product_id', 'launch_date']],
    on='product_id',
    how='left'
)
pre_launch_campaigns = marketing_with_launch[
    marketing_with_launch['start_date'] < marketing_with_launch['launch_date']
]
print(f"Removing {len(pre_launch_campaigns)} campaigns before product launch")
marketing_clean = marketing_with_launch[
    marketing_with_launch['start_date'] >= marketing_with_launch['launch_date']
].drop('launch_date', axis=1).copy()
cleaning_log.append(f"Removed {len(pre_launch_campaigns)} pre-launch campaigns")

print(f"✓ Temporal cleaning complete")
print()

# ============================================================================
# STEP 2: Sentiment Alignment
# ============================================================================
print("STEP 2: Sentiment Label Correction")
print("-" * 80)

def rating_to_sentiment(rating):
    """Convert rating to expected sentiment"""
    if rating >= 4.0:
        return 'Positive'
    elif rating <= 2.5:
        return 'Negative'
    else:
        return 'Neutral'

reviews_clean['expected_sentiment'] = reviews_clean['rating'].apply(rating_to_sentiment)
mismatched = reviews_clean[reviews_clean['sentiment'] != reviews_clean['expected_sentiment']]
print(f"Found {len(mismatched)} sentiment mismatches")

# DECISION: Use rating as ground truth (more objective than labels)
print(f"Decision: Using rating-based sentiment (ratings are more reliable)")
reviews_clean['sentiment_original'] = reviews_clean['sentiment']
reviews_clean['sentiment'] = reviews_clean['expected_sentiment']
reviews_clean = reviews_clean.drop('expected_sentiment', axis=1)
cleaning_log.append(f"Corrected {len(mismatched)} sentiment labels based on ratings")

print(f"✓ Sentiment alignment complete")
print()

# ============================================================================
# STEP 3: Comment Analysis & Flagging
# ============================================================================
print("STEP 3: Comment Template Detection")
print("-" * 80)

# Identify template comments
from collections import Counter
comment_freq = Counter(reviews_clean['comment'])
template_comments = {comment for comment, count in comment_freq.items() if count > 100}
print(f"Identified {len(template_comments)} template comments (used >100 times)")

# DECISION: Keep comments but flag them (they may still have signal)
reviews_clean['is_template'] = reviews_clean['comment'].isin(template_comments)
template_count = reviews_clean['is_template'].sum()
print(f"Flagged {template_count} reviews as template-based")
cleaning_log.append(f"Flagged {template_count} template comments")

# Create comment category feature
comment_categories = {
    'Packaging bocor saat diterima, kurang aman.': 'packaging_issue',
    'Kurang cocok di kulit saya, agak kering.': 'skin_reaction',
    'Wangi terlalu kuat untuk saya.': 'scent_complaint',
    'Mudah dibeli saat promo, value for money.': 'value_positive',
    'Harumnya tahan lama, suka banget!': 'scent_positive',
    'Kemasan baru lebih ramah lingkungan.': 'eco_friendly',
    'Memberikan hasil sesuai klaim after 2 weeks.': 'effectiveness',
    'Harga sesuai, kualitas oke.': 'value_neutral'
}
reviews_clean['comment_category'] = reviews_clean['comment'].map(comment_categories)

print(f"✓ Comment categorization complete")
print()

# ============================================================================
# STEP 4: Feature Engineering
# ============================================================================
print("STEP 4: Feature Engineering")
print("-" * 80)

# Product features
print("Adding product features...")
reviews_clean = reviews_clean.merge(
    products[['product_id', 'brand', 'type', 'base_price', 'launch_date']],
    on='product_id',
    how='left'
)

# Age features
reviews_clean['product_age_days'] = (reviews_clean['date'] - reviews_clean['launch_date']).dt.days
reviews_clean['review_year'] = reviews_clean['date'].dt.year
reviews_clean['review_month'] = reviews_clean['date'].dt.month
reviews_clean['review_day_of_week'] = reviews_clean['date'].dt.dayofweek

# Price tier
reviews_clean['price_tier'] = pd.cut(
    reviews_clean['base_price'],
    bins=[0, 25000, 35000, 50000],
    labels=['low', 'medium', 'high']
)

# Platform features (check for platform bias)
platform_avg_rating = reviews_clean.groupby('platform')['rating'].mean()
reviews_clean['platform_avg_rating'] = reviews_clean['platform'].map(platform_avg_rating)

print(f"✓ Added {7} new features")
print()

# ============================================================================
# STEP 5: Marketing Features
# ============================================================================
print("STEP 5: Marketing Feature Engineering")
print("-" * 80)

# Aggregate marketing data per product
marketing_agg = marketing_clean.groupby('product_id').agg({
    'spend_idr': 'sum',
    'engagement_rate': 'mean',
    'campaign_id': 'count'
}).rename(columns={
    'spend_idr': 'total_marketing_spend',
    'engagement_rate': 'avg_engagement_rate',
    'campaign_id': 'num_campaigns'
})

# Add channel diversity
channel_diversity = marketing_clean.groupby('product_id')['channel'].nunique()
marketing_agg['channel_diversity'] = channel_diversity

# Most used channel
most_used_channel = marketing_clean.groupby('product_id')['channel'].agg(
    lambda x: x.value_counts().index[0] if len(x) > 0 else 'none'
)
marketing_agg['primary_channel'] = most_used_channel

# Merge marketing features into reviews
reviews_clean = reviews_clean.merge(
    marketing_agg,
    on='product_id',
    how='left'
)

# Fill NaN for products with no marketing
reviews_clean['total_marketing_spend'] = reviews_clean['total_marketing_spend'].fillna(0)
reviews_clean['num_campaigns'] = reviews_clean['num_campaigns'].fillna(0)
reviews_clean['channel_diversity'] = reviews_clean['channel_diversity'].fillna(0)

print(f"✓ Added {5} marketing features")
print()

# ============================================================================
# STEP 6: Aggregate Product Metrics
# ============================================================================
print("STEP 6: Creating Product Performance Metrics")
print("-" * 80)

product_metrics = reviews_clean.groupby('product_id').agg({
    'rating': ['mean', 'std', 'count'],
    'sentiment': lambda x: (x == 'Positive').sum() / len(x),
    'is_template': 'mean'
}).round(3)

product_metrics.columns = [
    'avg_rating', 'rating_std', 'review_count',
    'positive_ratio', 'template_ratio'
]

# Add to reviews
reviews_clean = reviews_clean.merge(
    product_metrics[['avg_rating', 'positive_ratio']],
    on='product_id',
    how='left',
    suffixes=('', '_product')
)

print(f"✓ Added product-level aggregates")
print()

# ============================================================================
# STEP 7: Save Cleaned Data
# ============================================================================
print("=" * 80)
print("SAVING CLEANED DATASETS")
print("=" * 80)
print()

# Save cleaned files
reviews_clean.to_csv('reviews_cleaned.csv', index=False)
marketing_clean.to_csv('marketing_cleaned.csv', index=False)
products.to_csv('products_cleaned.csv', index=False)  # Products didn't need cleaning

print(f"✓ Saved reviews_cleaned.csv ({len(reviews_clean)} records)")
print(f"✓ Saved marketing_cleaned.csv ({len(marketing_clean)} records)")
print(f"✓ Saved products_cleaned.csv ({len(products)} records)")
print()

# ============================================================================
# STEP 8: Cleaning Summary Report
# ============================================================================
print("=" * 80)
print("CLEANING SUMMARY")
print("=" * 80)
print()

print("Data Reduction:")
print(f"  Reviews: {len(reviews)} → {len(reviews_clean)} ({(1-len(reviews_clean)/len(reviews))*100:.1f}% reduction)")
print(f"  Marketing: {len(marketing)} → {len(marketing_clean)} ({(1-len(marketing_clean)/len(marketing))*100:.1f}% reduction)")
print(f"  Products: {len(products)} → {len(products)} (no reduction)")
print()

print("Cleaning Operations Performed:")
for i, log_entry in enumerate(cleaning_log, 1):
    print(f"  {i}. {log_entry}")
print()

print("Features Added:")
print(f"  • Product features: brand, type, price, age")
print(f"  • Temporal features: year, month, day_of_week, product_age")
print(f"  • Marketing features: spend, campaigns, engagement, channels")
print(f"  • Comment features: category, is_template")
print(f"  • Aggregate features: product avg_rating, positive_ratio")
print()

print("Final Dataset Columns:")
print(f"  reviews_cleaned.csv: {len(reviews_clean.columns)} columns")
print(f"  {list(reviews_clean.columns)}")
print()

# Data quality metrics after cleaning
print("Data Quality After Cleaning:")
temporal_issues = len(reviews_clean[reviews_clean['date'] > TODAY]) + \
                  len(reviews_clean[reviews_clean['product_age_days'] < 0])
print(f"  ✓ Temporal issues: {temporal_issues} (0%)")
print(f"  ✓ Sentiment alignment: 100% (corrected based on ratings)")
print(f"  ✓ Template comments: Flagged but retained for analysis")
print(f"  ✓ All features engineered and ready for modeling")
print()

print("=" * 80)
print("READY FOR MODELING / ANALYSIS!")
print("=" * 80)
print()
print("Next steps:")
print("  1. Exploratory data analysis on cleaned data")
print("  2. Build predictive models (if applicable)")
print("  3. Generate insights and recommendations")
print("  4. Prepare competition submission")
print()
print("✓ Data cleaning pipeline complete!")
