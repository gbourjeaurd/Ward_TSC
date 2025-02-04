import pandas as pd
import networkx as nx
import community as community_louvain
import os

# Load the dataset
file_path = 
df = pd.read_csv(file_path)

# Convert Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')

# Define date ranges
date_ranges = {
    "name of date range": ('date', 'date'),
}

# Create results directory to save output
results_dir = 
os.makedirs(results_dir, exist_ok=True)

# Create network graphs
def create_network(df, start_date, end_date):
    # Filter by date range
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Create a bipartite graph from the filtered dataframe
    B = nx.Graph()
    for _, row in filtered_df.iterrows():
        B.add_edge(row['Buyer'], row['Title'])
    
    # Project the bipartite graph to a buyer-buyer network
    buyers = filtered_df['Buyer'].unique()
    G = nx.bipartite.weighted_projected_graph(B, buyers)
    
    return G

# Perform network analysis
def analyze_network(G, title):
    results = []
    results.append(f"\nAnalysis for {title}:\n")
    
    # Community detection using Louvain method
    partition = community_louvain.best_partition(G)
    modularity_score = community_louvain.modularity(partition, G)
    
    communities = {}
    for node, comm_id in partition.items():
        if comm_id not in communities:
            communities[comm_id] = []
        communities[comm_id].append(node)
    
    results.append(f"Number of communities: {len(communities)}")
    results.append(f"Modularity Score: {modularity_score:.4f}")
    for i, (comm_id, members) in enumerate(communities.items(), 1):
        subgraph = G.subgraph(members)
        results.append(f"Community {i} (edges: {subgraph.number_of_edges()}): {members}")
    
    # Identify Hubs and quantify degrees
    degrees = dict(G.degree())
    sorted_degrees = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:20]
    results.append(f"Top 20 hubs: {sorted_degrees}")

    # Calculate average degree centralities
    average_degree = sum(degrees.values()) / len(degrees)
    results.append(f"Average degree: {average_degree:.2f}")
    
    # Identify bridges by betweenness centrality
    betweenness = nx.betweenness_centrality(G)
    sorted_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:20]
    results.append(f"Top 20 nodes by betweenness centrality: {sorted_betweenness}")

    # Identify weak ties
    weak_ties = [(u, v) for u, v in G.edges if G.degree[u] == 1 or G.degree[v] == 1]
    results.append(f"Weak ties: {weak_ties}")
    results.append(f"Number of weak ties: {len(weak_ties)}")

# Perform network analysis for each date range
for title, (start_date, end_date) in date_ranges.items():
    G = create_network(df, start_date, end_date)
    analyze_network(G, title)
    
    # Save the network graph to a GraphML
    output_file = f'{results_dir}/network_{title.replace(" ", "_").replace("–", "-")}.graphml'
    
    # Add community attribute to nodes
    partition = community_louvain.best_partition(G)
    nx.set_node_attributes(G, partition, 'community')
    
    # Convert graph to a GraphML file
    nx.write_graphml(G, output_file)
    
    print(f"Network graph for {title} saved to {output_file}")