"""
customer_analysis.py
====================
Analisis Perilaku Pelanggan E-Commerce
- Segmentasi RFM (Recency, Frequency, Monetary)
- Analisis Retensi Kohort

Dependencies: pandas, matplotlib, numpy, seaborn
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# ── 0. REPRODUCIBILITY ──────────────────────────────────────────────────────
np.random.seed(42)

# ── 1. GENERATE SYNTHETIC DATASET ───────────────────────────────────────────
def generate_ecommerce_data(n_customers=1_000, n_orders=5_000):
    """
    Buat dataset sintetis transaksi e-commerce 2 tahun (Jan 2023 – Des 2024).
    Dataset sengaja memiliki dirty data: duplikat, nilai negatif, tanggal null.
    """
    customer_ids = [f"CUST{str(i).zfill(4)}" for i in range(1, n_customers + 1)]
    products     = ["Laptop Pro X1", "Wireless Headset", "Mechanical Keyboard",
                    "4K Monitor", "Gaming Chair", "USB-C Hub", "Webcam HD",
                    "External SSD", "Smart Speaker", "Desk Lamp LED"]
    categories   = {
        "Laptop Pro X1": "Electronics", "Wireless Headset": "Audio",
        "Mechanical Keyboard": "Peripherals", "4K Monitor": "Electronics",
        "Gaming Chair": "Furniture", "USB-C Hub": "Accessories",
        "Webcam HD": "Peripherals", "External SSD": "Storage",
        "Smart Speaker": "Audio", "Desk Lamp LED": "Accessories"
    }
    prices = {
        "Laptop Pro X1": 12_000_000, "Wireless Headset": 800_000,
        "Mechanical Keyboard": 1_200_000, "4K Monitor": 4_500_000,
        "Gaming Chair": 3_200_000, "USB-C Hub": 350_000,
        "Webcam HD": 750_000, "External SSD": 1_100_000,
        "Smart Speaker": 900_000, "Desk Lamp LED": 250_000
    }

    # Distribusi customer: 20% heavy buyers (> 10 orders), 80% casual
    weights = np.where(np.arange(n_customers) < n_customers * 0.2, 5, 1)
    weights = weights / weights.sum()

    orders = []
    start  = datetime(2023, 1, 1)
    end    = datetime(2024, 12, 31)
    span   = (end - start).days

    for _ in range(n_orders):
        cust    = np.random.choice(customer_ids, p=weights)
        product = np.random.choice(products)
        qty     = np.random.randint(1, 5)
        date    = start + timedelta(days=np.random.randint(0, span))

        # Inject dirty data ~12%
        dirty = np.random.random()
        if dirty < 0.04:
            date = None                          # null date
        elif dirty < 0.07:
            qty = -qty                           # negative qty
        elif dirty < 0.10:
            product = product + "!@#"            # corrupt product name
        elif dirty < 0.12:
            orders.append(orders[-1].copy() if orders else None)  # duplicate placeholder

        orders.append({
            "order_id":    f"ORD{np.random.randint(100000, 999999)}",
            "customer_id": cust,
            "order_date":  date,
            "product":     product,
            "category":    categories.get(product, "Unknown"),
            "quantity":    qty,
            "unit_price":  prices.get(product, 500_000),
            "discount_pct": np.random.choice([0, 5, 10, 15, 20],
                                              p=[0.5, 0.2, 0.15, 0.1, 0.05])
        })

    df = pd.DataFrame([o for o in orders if o is not None])
    return df


# ── 2. DATA CLEANING ─────────────────────────────────────────────────────────
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    raw_count = len(df)
    print(f"[CLEANING] Raw rows: {raw_count:,}")

    # Hapus duplikat order_id
    before = len(df)
    df = df.drop_duplicates(subset="order_id")
    print(f"  Duplikat dihapus: {before - len(df)}")

    # Hapus baris dengan tanggal null
    before = len(df)
    df = df.dropna(subset=["order_date"])
    print(f"  Baris tanggal null dihapus: {before - len(df)}")

    # Hapus qty negatif / nol
    before = len(df)
    df = df[df["quantity"] > 0]
    print(f"  Qty tidak valid dihapus: {before - len(df)}")

    # Bersihkan nama produk (hapus karakter non-alfanumerik di akhir)
    import re
    df["product"] = df["product"].apply(lambda x: re.sub(r'[^A-Za-z0-9 \-]', '', str(x)).strip())
    df["category"] = df["product"].map({
        "Laptop Pro X1": "Electronics", "Wireless Headset": "Audio",
        "Mechanical Keyboard": "Peripherals", "4K Monitor": "Electronics",
        "Gaming Chair": "Furniture", "USB-C Hub": "Accessories",
        "Webcam HD": "Peripherals", "External SSD": "Storage",
        "Smart Speaker": "Audio", "Desk Lamp LED": "Accessories"
    }).fillna("Unknown")
    df = df[df["category"] != "Unknown"]

    # Parse tanggal
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Hitung revenue
    df["revenue"] = df["unit_price"] * df["quantity"] * (1 - df["discount_pct"] / 100)

    clean_count = len(df)
    print(f"[CLEANING] Clean rows: {clean_count:,}  "
          f"({(raw_count - clean_count)/raw_count*100:.1f}% removed)\n")
    return df.reset_index(drop=True)


# ── 3. RFM SEGMENTATION ───────────────────────────────────────────────────────
def compute_rfm(df: pd.DataFrame, snapshot_date=None) -> pd.DataFrame:
    if snapshot_date is None:
        snapshot_date = df["order_date"].max() + timedelta(days=1)

    rfm = df.groupby("customer_id").agg(
        recency   = ("order_date", lambda x: (snapshot_date - x.max()).days),
        frequency = ("order_id",   "nunique"),
        monetary  = ("revenue",    "sum")
    ).reset_index()

    # Scoring 1–5 per dimensi (quintile)
    rfm["R"] = pd.qcut(rfm["recency"],   5, labels=[5,4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M"] = pd.qcut(rfm["monetary"],  5, labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_Score"] = rfm["R"].astype(str) + rfm["F"].astype(str) + rfm["M"].astype(str)
    rfm["RFM_Total"] = rfm[["R","F","M"]].sum(axis=1)

    # Segmentasi
    def segment(row):
        r, f, m = row["R"], row["F"], row["M"]
        if r >= 4 and f >= 4 and m >= 4:  return "Champions"
        if r >= 3 and f >= 3:              return "Loyal Customers"
        if r >= 4 and f <= 2:             return "Recent Customers"
        if r >= 3 and f >= 1 and m >= 3:  return "Potential Loyalists"
        if r == 2 and f >= 2:             return "At Risk"
        if r <= 2 and f <= 2 and m >= 3:  return "Can't Lose Them"
        if r <= 2 and f <= 2:             return "Lost Customers"
        return "Others"

    rfm["Segment"] = rfm.apply(segment, axis=1)
    print(f"[RFM] Total pelanggan tersegmentasi: {len(rfm):,}")
    print(rfm["Segment"].value_counts().to_string())
    print()
    return rfm


# ── 4. COHORT RETENTION ANALYSIS ─────────────────────────────────────────────
def compute_cohort(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["order_month"] = df["order_date"].dt.to_period("M")

    # Cohort = bulan pertama beli
    df["cohort"] = df.groupby("customer_id")["order_date"] \
                     .transform("min").dt.to_period("M")

    df["period_number"] = (df["order_month"] - df["cohort"]).apply(lambda x: x.n)

    cohort_data = df.groupby(["cohort", "period_number"])["customer_id"] \
                    .nunique().reset_index()
    cohort_pivot = cohort_data.pivot(index="cohort", columns="period_number",
                                     values="customer_id")

    # Retention rate relative to cohort size (period 0)
    cohort_size  = cohort_pivot[0]
    retention    = cohort_pivot.div(cohort_size, axis=0).round(3) * 100

    print(f"[COHORT] Cohorts: {len(retention)}  |  Max period: {retention.columns.max()}")
    return retention, cohort_size


# ── 5. VISUALISASI ────────────────────────────────────────────────────────────
PALETTE  = ["#4ade80", "#22c55e", "#16a34a", "#15803d", "#166534",
             "#f87171", "#fbbf24", "#60a5fa", "#a78bfa", "#fb923c"]
BG_DARK  = "#1a1f2e"
CARD_BG  = "#252d3d"
TEXT_CLR = "#d1d5db"
GRID_CLR = "#2d3748"

plt.rcParams.update({
    "figure.facecolor": BG_DARK, "axes.facecolor": CARD_BG,
    "axes.edgecolor": GRID_CLR,  "axes.labelcolor": TEXT_CLR,
    "xtick.color": "#9ca3af",    "ytick.color": "#9ca3af",
    "text.color": TEXT_CLR,      "grid.color": GRID_CLR,
    "font.family": "DejaVu Sans","font.size": 9,
})


def plot_rfm_segment_distribution(rfm: pd.DataFrame, save_path="output/rfm_segments.png"):
    seg_counts = rfm["Segment"].value_counts()
    colors_map = {
        "Champions":           "#4ade80",
        "Loyal Customers":     "#22c55e",
        "Potential Loyalists": "#86efac",
        "Recent Customers":    "#fbbf24",
        "At Risk":             "#f87171",
        "Can't Lose Them":    "#fb923c",
        "Lost Customers":      "#ef4444",
        "Others":              "#6b7280",
    }
    colors = [colors_map.get(s, "#6b7280") for s in seg_counts.index]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor=BG_DARK)
    fig.suptitle("Segmentasi RFM Pelanggan E-Commerce", fontsize=14,
                 fontweight="bold", color="white", y=1.01)

    # Donut chart
    ax1 = axes[0]
    wedges, texts, autotexts = ax1.pie(
        seg_counts, labels=seg_counts.index, colors=colors,
        autopct="%1.1f%%", startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor=BG_DARK, linewidth=2)
    )
    for t in texts:    t.set(color=TEXT_CLR, fontsize=8)
    for at in autotexts: at.set(color="white", fontsize=7, fontweight="bold")
    ax1.set_title("Distribusi Segmen Pelanggan", color="white", fontsize=11, pad=12)

    # Horizontal bar chart
    ax2 = axes[1]
    ax2.set_facecolor(CARD_BG)
    bars = ax2.barh(seg_counts.index[::-1], seg_counts.values[::-1],
                    color=colors[::-1], edgecolor="none", height=0.6)
    for bar, val in zip(bars, seg_counts.values[::-1]):
        ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                 f"{val:,}", va="center", color=TEXT_CLR, fontsize=8)
    ax2.set_xlabel("Jumlah Pelanggan", color=TEXT_CLR)
    ax2.set_title("Jumlah Pelanggan per Segmen", color="white", fontsize=11, pad=12)
    ax2.grid(axis="x", color=GRID_CLR, linewidth=0.5)
    ax2.spines[:].set_color(GRID_CLR)
    ax2.set_xlim(0, seg_counts.max() * 1.18)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    plt.close()
    print(f"[PLOT] Saved → {save_path}")


def plot_rfm_scatter(rfm: pd.DataFrame, save_path="output/rfm_scatter.png"):
    fig, ax = plt.subplots(figsize=(10, 6), facecolor=BG_DARK)
    ax.set_facecolor(CARD_BG)

    seg_colors = {
        "Champions":           "#4ade80",
        "Loyal Customers":     "#22c55e",
        "Potential Loyalists": "#86efac",
        "Recent Customers":    "#fbbf24",
        "At Risk":             "#f87171",
        "Can't Lose Them":    "#fb923c",
        "Lost Customers":      "#ef4444",
        "Others":              "#6b7280",
    }
    for seg, grp in rfm.groupby("Segment"):
        ax.scatter(grp["recency"], grp["monetary"] / 1e6,
                   s=grp["frequency"] * 12, alpha=0.65,
                   color=seg_colors.get(seg, "#6b7280"),
                   label=seg, edgecolors="none")

    ax.set_xlabel("Recency (hari sejak pembelian terakhir)", color=TEXT_CLR)
    ax.set_ylabel("Monetary (Juta Rp)", color=TEXT_CLR)
    ax.set_title("RFM Scatter: Recency vs Monetary (ukuran = Frequency)",
                 color="white", fontsize=12, pad=12)
    ax.legend(loc="upper right", fontsize=7.5, framealpha=0.2,
              labelcolor=TEXT_CLR, facecolor=CARD_BG, edgecolor=GRID_CLR)
    ax.grid(color=GRID_CLR, linewidth=0.5)
    ax.spines[:].set_color(GRID_CLR)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp{x:.0f}M"))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    plt.close()
    print(f"[PLOT] Saved → {save_path}")


def plot_cohort_heatmap(retention: pd.DataFrame, save_path="output/cohort_heatmap.png"):
    # Ambil 12 cohort & 12 periode
    ret = retention.iloc[:12, :13]

    fig, ax = plt.subplots(figsize=(14, 7), facecolor=BG_DARK)
    ax.set_facecolor(BG_DARK)

    cmap = sns.color_palette("Greens", as_cmap=True)
    sns.heatmap(
        ret, ax=ax, annot=True, fmt=".0f", cmap=cmap,
        linewidths=0.5, linecolor="#1a1f2e",
        cbar_kws={"label": "Retention Rate (%)", "shrink": 0.6},
        annot_kws={"size": 8, "color": "white"},
        vmin=0, vmax=100
    )

    ax.set_title("Analisis Retensi Kohort Bulanan (%)",
                 color="white", fontsize=13, pad=14, fontweight="bold")
    ax.set_xlabel("Period (bulan setelah akuisisi)", color=TEXT_CLR, labelpad=8)
    ax.set_ylabel("Cohort (bulan pertama beli)", color=TEXT_CLR, labelpad=8)
    ax.tick_params(axis="x", colors=TEXT_CLR, labelsize=8)
    ax.tick_params(axis="y", colors=TEXT_CLR, labelsize=8, rotation=0)

    # Colorbar styling
    cbar = ax.collections[0].colorbar
    cbar.ax.yaxis.label.set_color(TEXT_CLR)
    cbar.ax.tick_params(colors=TEXT_CLR)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    plt.close()
    print(f"[PLOT] Saved → {save_path}")


def plot_monthly_revenue(df: pd.DataFrame, save_path="output/monthly_revenue.png"):
    monthly = df.groupby(df["order_date"].dt.to_period("M"))["revenue"] \
                .sum().reset_index()
    monthly["order_date"] = monthly["order_date"].dt.to_timestamp()
    monthly["rev_m"] = monthly["revenue"] / 1e6

    fig, ax = plt.subplots(figsize=(13, 5), facecolor=BG_DARK)
    ax.set_facecolor(CARD_BG)

    ax.fill_between(monthly["order_date"], monthly["rev_m"],
                    alpha=0.15, color="#4ade80")
    ax.plot(monthly["order_date"], monthly["rev_m"],
            color="#4ade80", linewidth=2.5, marker="o", markersize=4)

    ax.set_title("Tren Revenue Bulanan (Jan 2023 – Des 2024)",
                 color="white", fontsize=12, pad=12, fontweight="bold")
    ax.set_xlabel("Bulan", color=TEXT_CLR)
    ax.set_ylabel("Revenue (Juta Rp)", color=TEXT_CLR)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"Rp{x:.0f}M"))
    ax.grid(color=GRID_CLR, linewidth=0.5)
    ax.spines[:].set_color(GRID_CLR)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight", facecolor=BG_DARK)
    plt.close()
    print(f"[PLOT] Saved → {save_path}")


# ── 6. MAIN ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    os.makedirs("output", exist_ok=True)

    print("=" * 60)
    print("  ANALISIS PERILAKU PELANGGAN E-COMMERCE")
    print("  RFM Segmentation + Cohort Retention")
    print("=" * 60 + "\n")

    # Step 1: Generate & save raw data
    print("[STEP 1] Generating synthetic dataset...")
    df_raw = generate_ecommerce_data(n_customers=1_000, n_orders=5_000)
    df_raw.to_csv("dataset_raw/ecommerce_raw.csv", index=False)
    print(f"  Raw data saved: {len(df_raw):,} rows\n")

    # Step 2: Clean data
    print("[STEP 2] Cleaning data...")
    df_clean = clean_data(df_raw)
    df_clean.to_csv("dataset_clean/ecommerce_clean.csv", index=False)

    # Step 3: RFM
    print("[STEP 3] Computing RFM scores...")
    rfm = compute_rfm(df_clean)
    rfm.to_csv("output/rfm_results.csv", index=False)

    # Step 4: Cohort
    print("[STEP 4] Computing cohort retention...")
    retention, cohort_size = compute_cohort(df_clean)
    retention.to_csv("output/cohort_retention.csv")

    # Step 5: Plots
    print("[STEP 5] Generating visualizations...")
    plot_rfm_segment_distribution(rfm)
    plot_rfm_scatter(rfm)
    plot_cohort_heatmap(retention)
    plot_monthly_revenue(df_clean)

    print("\n✅ Analisis selesai! Output tersimpan di folder output/")
    print("=" * 60)
