import os
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from sklearn.cluster import KMeans
import umap.umap_ as umap
from scipy.spatial import ConvexHull
import numpy as np

matplotlib.use("Agg")
sns.set_theme()

def generate_visualizations():
    # Load data
    db_path = "resources/normanpd.db"
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM incidents", conn)
    conn.close()

    static_dir = os.path.join(os.getcwd(), "static")
    os.makedirs(static_dir, exist_ok=True)

    # -------------------------------------------------------------------
    # SIMPLE CLUSTERING WITH K-MEANS

    # Use a set of top natures and locations
    top_natures = df["Nature"].value_counts().head(50).index
    top_locations = df["Location"].value_counts().head(50).index

    filtered_df = df[df["Location"].isin(top_locations) & df["Nature"].isin(top_natures)]
    pivot_table = pd.crosstab(filtered_df["Nature"], filtered_df["Location"])

    # Use UMAP for dimensionality reduction
    reducer = umap.UMAP(random_state=42, n_neighbors=10, min_dist=0.05)
    embedding = reducer.fit_transform(pivot_table)

    # Apply K-Means Clustering (adjust n_clusters as needed)
    kmeans = KMeans(n_clusters=7, random_state=42)
    labels = kmeans.fit_predict(embedding)

    # Each row in pivot_table corresponds to one Nature
    nature_list = pivot_table.index.tolist()
    cluster_natures = {c: [] for c in np.unique(labels)}
    for nature, cluster_label in zip(nature_list, labels):
        cluster_natures[cluster_label].append(nature)

    # Summarize each cluster by top N natures or common patterns:
    # For simplicity, let's find the top 3 most common natures within each cluster.
    # Since each row in pivot_table represents a Nature, we already know they are unique per row.
    # Another approach: we can look back at 'filtered_df' and see how often these natures occur overall.
    cluster_labels_map = {}
    for c, n_list in cluster_natures.items():
        # Count how often each nature occurs in the filtered_df
        # filtered_df only includes top natures/locations, so counting occurrences is direct:
        cluster_df = filtered_df[filtered_df["Nature"].isin(n_list)]
        top_n_in_cluster = cluster_df["Nature"].value_counts().head(3).index.tolist()
        # Create a descriptive label
        cluster_label_str = ", ".join(top_n_in_cluster)
        cluster_labels_map[c] = cluster_label_str

    # Plot K-Means results
    kmeans_path = os.path.join(static_dir, "kmeans_cluster_umap.png")
    plt.figure(figsize=(8, 6))  # Slightly smaller figure for a "zoomed-in" feel

    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels)
    cluster_palette = sns.color_palette("Set2", n_colors=n_clusters)

    # Plot each cluster
    for label_val in unique_labels:
        idx = (labels == label_val)
        plt.scatter(embedding[idx, 0], embedding[idx, 1],
                    color=cluster_palette[label_val],
                    marker='o', label=f"Cluster {label_val}", alpha=0.8, s=100, edgecolors='black', linewidth=0.5)

        points = embedding[idx]
        if len(points) > 2:
            hull = ConvexHull(points)
            hull_points = points[hull.vertices]
            plt.plot(hull_points[:, 0], hull_points[:, 1], color=cluster_palette[label_val], linewidth=2)
            plt.fill(hull_points[:, 0], hull_points[:, 1], cluster_palette[label_val], alpha=0.1)

    # Plot cluster centroids
    centers = kmeans.cluster_centers_
    plt.scatter(centers[:, 0], centers[:, 1],
                c='black', s=200, marker='*', edgecolors='white', linewidth=1, label='Centroids')

    # Annotate clusters with descriptive text
    for c_idx, (x, y) in enumerate(centers):
        text_label = cluster_labels_map.get(c_idx, f"Cluster {c_idx}")
        plt.text(x, y, text_label, fontsize=9, ha='center', va='center', color='white',
                 bbox=dict(facecolor='black', alpha=0.6, boxstyle='round,pad=0.5'))

    # Adjust plot limits
    x_min, x_max = embedding[:, 0].min(), embedding[:, 0].max()
    y_min, y_max = embedding[:, 1].min(), embedding[:, 1].max()
    x_margin = (x_max - x_min) * 0.1
    y_margin = (y_max - y_min) * 0.1
    plt.xlim(x_min - x_margin, x_max + x_margin)
    plt.ylim(y_min - y_margin, y_max + y_margin)

    plt.title("K-Means Clustering of Incident Natures (UMAP Reduced)", fontsize=16)
    plt.xlabel("UMAP-1", fontsize=12)
    plt.ylabel("UMAP-2", fontsize=12)
    plt.legend(title="Cluster Groups", loc='best')
    plt.tight_layout()
    plt.savefig(kmeans_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------------
    # BAR CHART (COMPARISON)
    top20_natures = df["Nature"].value_counts().head(20)
    bar_chart_path = os.path.join(static_dir, "bar_chart.png")
    plt.figure(figsize=(12, 6))
    top20_natures.plot(kind="bar", color="skyblue")
    plt.title("Top 20 Incident Nature Counts", fontsize=16)
    plt.xlabel("Incident Nature", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(bar_chart_path, dpi=300)
    plt.close()

    # -------------------------------------------------------------------
    # STACKED BAR CHART (ANOTHER VISUALIZATION)
    top10_natures = df["Nature"].value_counts().head(10).index
    top10_locations = df["Location"].value_counts().head(10).index
    filtered_df2 = df[df["Location"].isin(top10_locations) & df["Nature"].isin(top10_natures)]
    pivot_table_2 = pd.crosstab(filtered_df2["Location"], filtered_df2["Nature"])

    heatmap_path = os.path.join(static_dir, "heatmap.png")
    plt.figure(figsize=(12, 6))
    sns.heatmap(pivot_table_2, annot=True, fmt="d", cmap="YlGnBu")
    plt.title("Heatmap of Top 10 Natures Across Top 10 Locations", fontsize=16)
    plt.xlabel("Nature", fontsize=12)
    plt.ylabel("Location", fontsize=12)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(heatmap_path, dpi=300)
    plt.close()

    return {
        'kmeans_cluster_umap': kmeans_path,
        'bar': bar_chart_path,
        'heatmap': heatmap_path
    }
