#!/usr/bin/env python3
"""
Comprehensive Dataset Analysis
Analyzing FMCG Personal Care Synthetic Dataset
"""

import pandas as pd
import numpy as np
from collections import Counter
import sys

print("="*80)
print("ANALISIS LENGKAP DATASET FMCG PERSONAL CARE")
print("="*80)

# ============================================================================
# 1. LOAD DATA
# ============================================================================
print("\n[STEP 1] Loading datasets...")
try:
    df_products = pd.read_csv('products.csv')
    df_reviews = pd.read_csv('reviews.csv')
    df_marketing = pd.read_csv('marketing.csv')
    print("✓ products.csv loaded:", df_products.shape)
    print("✓ reviews.csv loaded:", df_reviews.shape)
    print("✓ marketing.csv loaded:", df_marketing.shape)
except Exception as e:
    print(f"✗ Error loading data: {e}")
    sys.exit(1)

# ============================================================================
# 2. DATA STRUCTURE EXPLORATION
# ============================================================================
print("\n" + "="*80)
print("[STEP 2] DATA STRUCTURE EXPLORATION")
print("="*80)

print("\n--- PRODUCTS.CSV ---")
print(f"Columns: {list(df_products.columns)}")
print(f"Shape: {df_products.shape}")
print(f"Brands: {df_products['brand'].unique().tolist()}")
print(f"Types: {df_products['type'].unique().tolist()}")
print(f"\nSample data:")
print(df_products.head(3))

print("\n--- REVIEWS.CSV ---")
print(f"Columns: {list(df_reviews.columns)}")
print(f"Shape: {df_reviews.shape}")
print(f"Date range: {df_reviews['date'].min()} to {df_reviews['date'].max()}")
print(f"Rating range: {df_reviews['rating'].min()} to {df_reviews['rating'].max()}")
print(f"Platforms: {df_reviews['platform'].unique().tolist()}")

# ============================================================================
# 3. DUPLICATE CHECK (CRITICAL!)
# ============================================================================
print("\n" + "="*80)
print("[STEP 3] DUPLICATE ANALYSIS - SILVER BULLET TEST")
print("="*80)

print("\n--- REVIEWS.CSV DUPLICATE CHECK ---")
print("Testing untuk duplikat TANPA review_id (seharusnya unique)")

# Exclude review_id untuk cek duplikat
cols_to_check = [col for col in df_reviews.columns if col != 'review_id']
duplicates = df_reviews.duplicated(subset=cols_to_check, keep=False)
num_duplicates = duplicates.sum()

print(f"\nTotal rows: {len(df_reviews)}")
print(f"Duplicate rows (excluding review_id): {num_duplicates}")

if num_duplicates > 0:
    print(f"\n❌ TERBUKTI: {num_duplicates} duplikat ditemukan!")
    print("Dataset reviews.csv adalah SINTETIS dan LAZY GENERATED")

    # Show duplicate examples
    dup_rows = df_reviews[duplicates].sort_values(by=cols_to_check)
    print("\nContoh duplikat:")
    print(dup_rows[['product_id', 'date', 'rating', 'comment', 'platform']].head(10))

    # Find exact duplicate groups
    print("\nMencari grup duplikat yang identik...")
    dup_groups = df_reviews[duplicates].groupby(cols_to_check).size().reset_index(name='count')
    dup_groups = dup_groups[dup_groups['count'] > 1].sort_values('count', ascending=False)
    print(f"Jumlah grup duplikat: {len(dup_groups)}")
    if len(dup_groups) > 0:
        print("\nTop 5 grup duplikat:")
        print(dup_groups.head())
else:
    print("\n✓ Tidak ada duplikat ditemukan")

# ============================================================================
# 4. REVIEW QUALITY ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("[STEP 4] REVIEW QUALITY ANALYSIS")
print("="*80)

# Check comment-rating consistency
print("\n--- Sentiment vs Rating Consistency ---")
df_reviews['expected_sentiment'] = df_reviews['rating'].apply(
    lambda x: 'Positive' if x >= 4 else ('Negative' if x <= 2 else 'Neutral')
)
mismatches = (df_reviews['sentiment'] != df_reviews['expected_sentiment']).sum()
print(f"Mismatch antara sentiment dan rating: {mismatches} ({mismatches/len(df_reviews)*100:.2f}%)")

if mismatches > len(df_reviews) * 0.1:  # >10% mismatch
    print("❌ WARNING: Terlalu banyak inkonsistensi sentiment-rating!")
    print("Ini menunjukkan data generator yang RUSAK")

# Check comment diversity
print("\n--- Comment Diversity ---")
unique_comments = df_reviews['comment'].nunique()
total_comments = len(df_reviews)
print(f"Unique comments: {unique_comments}")
print(f"Total comments: {total_comments}")
print(f"Diversity ratio: {unique_comments/total_comments:.2%}")

if unique_comments/total_comments < 0.5:
    print("❌ WARNING: Comment diversity terlalu rendah!")
    print("Banyak comment yang sama persis - ciri data SINTETIS")

# Most common comments
print("\nTop 10 comments paling sering muncul:")
comment_counts = df_reviews['comment'].value_counts().head(10)
for comment, count in comment_counts.items():
    print(f"  [{count}x] {comment[:60]}...")

# ============================================================================
# 5. TEMPORAL PATTERN ANALYSIS
# ============================================================================
print("\n" + "="*80)
print("[STEP 5] TEMPORAL PATTERN ANALYSIS")
print("="*80)

df_reviews['date'] = pd.to_datetime(df_reviews['date'])
df_reviews['year'] = df_reviews['date'].dt.year
df_reviews['month'] = df_reviews['date'].dt.month
df_reviews['quarter'] = df_reviews['date'].dt.quarter

# Reviews per year
print("\n--- Reviews per Year ---")
print(df_reviews['year'].value_counts().sort_index())

# Reviews per quarter
print("\n--- Reviews per Quarter (all years combined) ---")
print(df_reviews['quarter'].value_counts().sort_index())

# Check temporal distribution uniformity
quarterly_counts = df_reviews.groupby(['year', 'quarter']).size()
print(f"\n--- Quarterly Distribution Statistics ---")
print(f"Mean: {quarterly_counts.mean():.2f}")
print(f"Std: {quarterly_counts.std():.2f}")
print(f"Coefficient of Variation: {quarterly_counts.std()/quarterly_counts.mean():.3f}")

if quarterly_counts.std()/quarterly_counts.mean() < 0.1:
    print("❌ WARNING: Distribusi temporal terlalu UNIFORM!")
    print("Data nyata seharusnya punya variasi natural yang lebih besar")

# ============================================================================
# 6. FINAL CONCLUSION
# ============================================================================
print("\n" + "="*80)
print("[STEP 6] KESIMPULAN ANALISIS")
print("="*80)

issues_found = []

if num_duplicates > 0:
    issues_found.append(f"Duplikat di reviews.csv: {num_duplicates} rows")

if mismatches > len(df_reviews) * 0.1:
    issues_found.append(f"Sentiment-rating mismatch: {mismatches/len(df_reviews)*100:.1f}%")

if unique_comments/total_comments < 0.5:
    issues_found.append(f"Comment diversity rendah: {unique_comments/total_comments:.1%}")

if quarterly_counts.std()/quarterly_counts.mean() < 0.1:
    issues_found.append(f"Distribusi temporal terlalu uniform (CV: {quarterly_counts.std()/quarterly_counts.mean():.3f})")

if issues_found:
    print("\n❌ DATASET BERMASALAH!")
    print("\nIssues ditemukan:")
    for i, issue in enumerate(issues_found, 1):
        print(f"{i}. {issue}")
    print("\n🎯 KESIMPULAN: Dataset ini adalah SINTETIS dengan KUALITAS RENDAH")
    print("   Generator data memiliki BUG dan INKONSISTENSI")
else:
    print("\n✓ Dataset tampak VALID")

print("\n" + "="*80)
print("CATATAN: Analisis SALES.CSV diperlukan untuk validasi lengkap pola musiman!")
print("="*80)
