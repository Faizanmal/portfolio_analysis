"""
Graph Neural Networks
=====================

Graph neural networks for financial relationship analysis:
- Portfolio as graph representation
- Asset relationship modeling
- Supply chain networks
- Market correlation graphs
- GNN-based predictions
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging


class EdgeType(Enum):
    """Types of edges in financial graphs"""
    CORRELATION = "correlation"
    SECTOR = "sector"
    SUPPLY_CHAIN = "supply_chain"
    OWNERSHIP = "ownership"
    COMPETITOR = "competitor"
    SUBSIDIARY = "subsidiary"
    SIMILAR = "similar"


class NodeType(Enum):
    """Types of nodes in financial graphs"""
    ASSET = "asset"
    SECTOR = "sector"
    COMPANY = "company"
    PORTFOLIO = "portfolio"
    FACTOR = "factor"


@dataclass
class GraphNode:
    """Node in a financial graph"""
    node_id: str
    node_type: NodeType
    features: np.ndarray
    
    # Metadata
    name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphEdge:
    """Edge in a financial graph"""
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0
    
    # Edge features
    features: Optional[np.ndarray] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PortfolioGraph:
    """
    Represents a portfolio as a graph for GNN analysis.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("portfolio_graph")
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.adjacency: Dict[str, List[str]] = {}
    
    def add_node(self, node: GraphNode):
        """Add a node to the graph"""
        self.nodes[node.node_id] = node
        if node.node_id not in self.adjacency:
            self.adjacency[node.node_id] = []
    
    def add_edge(self, edge: GraphEdge):
        """Add an edge to the graph"""
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            self.logger.warning(f"Edge references unknown node(s)")
            return
        
        self.edges.append(edge)
        self.adjacency[edge.source_id].append(edge.target_id)
        # For undirected graphs, add reverse edge
        if edge.target_id not in self.adjacency:
            self.adjacency[edge.target_id] = []
        self.adjacency[edge.target_id].append(edge.source_id)
    
    def get_node_features_matrix(self) -> Tuple[np.ndarray, List[str]]:
        """Get node features as a matrix"""
        node_ids = list(self.nodes.keys())
        features = np.stack([self.nodes[nid].features for nid in node_ids])
        return features, node_ids
    
    def get_adjacency_matrix(self) -> Tuple[np.ndarray, List[str]]:
        """Get adjacency matrix"""
        node_ids = list(self.nodes.keys())
        n = len(node_ids)
        id_to_idx = {nid: i for i, nid in enumerate(node_ids)}
        
        adj = np.zeros((n, n))
        for edge in self.edges:
            i = id_to_idx[edge.source_id]
            j = id_to_idx[edge.target_id]
            adj[i, j] = edge.weight
            adj[j, i] = edge.weight  # Symmetric
        
        return adj, node_ids
    
    def get_edge_index(self) -> Tuple[np.ndarray, List[str]]:
        """Get edge index in COO format (for PyTorch Geometric)"""
        node_ids = list(self.nodes.keys())
        id_to_idx = {nid: i for i, nid in enumerate(node_ids)}
        
        sources = []
        targets = []
        
        for edge in self.edges:
            sources.append(id_to_idx[edge.source_id])
            targets.append(id_to_idx[edge.target_id])
            # Add reverse for undirected
            sources.append(id_to_idx[edge.target_id])
            targets.append(id_to_idx[edge.source_id])
        
        edge_index = np.array([sources, targets])
        return edge_index, node_ids
    
    def build_from_correlation_matrix(
        self,
        symbols: List[str],
        features: np.ndarray,
        correlation_matrix: np.ndarray,
        threshold: float = 0.5
    ):
        """Build graph from correlation matrix"""
        n = len(symbols)
        
        # Add nodes
        for i, symbol in enumerate(symbols):
            node = GraphNode(
                node_id=symbol,
                node_type=NodeType.ASSET,
                features=features[i],
                name=symbol
            )
            self.add_node(node)
        
        # Add edges for significant correlations
        for i in range(n):
            for j in range(i + 1, n):
                corr = correlation_matrix[i, j]
                if abs(corr) >= threshold:
                    edge = GraphEdge(
                        source_id=symbols[i],
                        target_id=symbols[j],
                        edge_type=EdgeType.CORRELATION,
                        weight=corr
                    )
                    self.add_edge(edge)
        
        self.logger.info(f"Built graph with {len(self.nodes)} nodes, {len(self.edges)} edges")
    
    def build_from_sectors(
        self,
        assets: List[Dict[str, Any]]
    ):
        """Build graph connecting assets in same sectors"""
        sectors = {}
        
        for asset in assets:
            symbol = asset['symbol']
            sector = asset.get('sector', 'Unknown')
            
            # Add asset node
            node = GraphNode(
                node_id=symbol,
                node_type=NodeType.ASSET,
                features=np.array(asset.get('features', [0])),
                name=symbol,
                metadata={'sector': sector}
            )
            self.add_node(node)
            
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(symbol)
        
        # Add edges between assets in same sector
        for sector, sector_assets in sectors.items():
            for i, asset1 in enumerate(sector_assets):
                for asset2 in sector_assets[i+1:]:
                    edge = GraphEdge(
                        source_id=asset1,
                        target_id=asset2,
                        edge_type=EdgeType.SECTOR,
                        weight=1.0,
                        metadata={'sector': sector}
                    )
                    self.add_edge(edge)
    
    def get_neighbors(self, node_id: str, hops: int = 1) -> Set[str]:
        """Get neighbors within k hops"""
        visited = {node_id}
        current_layer = {node_id}
        
        for _ in range(hops):
            next_layer = set()
            for node in current_layer:
                for neighbor in self.adjacency.get(node, []):
                    if neighbor not in visited:
                        next_layer.add(neighbor)
                        visited.add(neighbor)
            current_layer = next_layer
        
        visited.remove(node_id)
        return visited
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation"""
        return {
            'nodes': [
                {
                    'id': n.node_id,
                    'type': n.node_type.value,
                    'name': n.name,
                    'features_shape': n.features.shape
                }
                for n in self.nodes.values()
            ],
            'edges': [
                {
                    'source': e.source_id,
                    'target': e.target_id,
                    'type': e.edge_type.value,
                    'weight': e.weight
                }
                for e in self.edges
            ],
            'num_nodes': len(self.nodes),
            'num_edges': len(self.edges)
        }


class GNNLayer:
    """
    Graph neural network layer implementation.
    """
    
    def __init__(
        self,
        in_features: int,
        out_features: int,
        activation: str = 'relu'
    ):
        self.in_features = in_features
        self.out_features = out_features
        self.activation = activation
        
        # Initialize weights
        self.W = np.random.randn(in_features, out_features) * np.sqrt(2.0 / in_features)
        self.b = np.zeros(out_features)
    
    def forward(
        self,
        node_features: np.ndarray,
        adjacency: np.ndarray
    ) -> np.ndarray:
        """
        Forward pass through GNN layer.
        Uses message passing with neighborhood aggregation.
        """
        # Normalize adjacency (add self-loops and normalize)
        n = adjacency.shape[0]
        adj_self = adjacency + np.eye(n)
        degree = np.sum(adj_self, axis=1)
        degree_inv_sqrt = np.power(degree, -0.5)
        degree_inv_sqrt[np.isinf(degree_inv_sqrt)] = 0
        D_inv_sqrt = np.diag(degree_inv_sqrt)
        
        # Symmetric normalization
        adj_normalized = D_inv_sqrt @ adj_self @ D_inv_sqrt
        
        # Message passing: aggregate neighbor features
        aggregated = adj_normalized @ node_features
        
        # Transform
        output = aggregated @ self.W + self.b
        
        # Activation
        if self.activation == 'relu':
            output = np.maximum(0, output)
        elif self.activation == 'sigmoid':
            output = 1 / (1 + np.exp(-output))
        elif self.activation == 'tanh':
            output = np.tanh(output)
        
        return output


class GraphNeuralNetwork:
    """
    Multi-layer graph neural network.
    """
    
    def __init__(
        self,
        layer_dims: List[int],
        dropout: float = 0.1
    ):
        self.logger = logging.getLogger("gnn")
        self.layers: List[GNNLayer] = []
        self.dropout = dropout
        
        # Build layers
        for i in range(len(layer_dims) - 1):
            activation = 'relu' if i < len(layer_dims) - 2 else 'none'
            layer = GNNLayer(
                layer_dims[i],
                layer_dims[i + 1],
                activation=activation
            )
            self.layers.append(layer)
        
        self.logger.info(f"Built GNN with {len(self.layers)} layers")
    
    def forward(
        self,
        node_features: np.ndarray,
        adjacency: np.ndarray,
        training: bool = False
    ) -> np.ndarray:
        """Forward pass through all layers"""
        x = node_features
        
        for i, layer in enumerate(self.layers):
            x = layer.forward(x, adjacency)
            
            # Apply dropout during training (except last layer)
            if training and i < len(self.layers) - 1:
                mask = np.random.binomial(1, 1 - self.dropout, x.shape)
                x = x * mask / (1 - self.dropout)
        
        return x
    
    def predict_node_labels(
        self,
        node_features: np.ndarray,
        adjacency: np.ndarray
    ) -> np.ndarray:
        """Predict labels for each node"""
        logits = self.forward(node_features, adjacency, training=False)
        # Softmax
        exp_logits = np.exp(logits - np.max(logits, axis=1, keepdims=True))
        probs = exp_logits / np.sum(exp_logits, axis=1, keepdims=True)
        return probs
    
    def predict_link(
        self,
        node_features: np.ndarray,
        adjacency: np.ndarray,
        node1_idx: int,
        node2_idx: int
    ) -> float:
        """Predict link probability between two nodes"""
        embeddings = self.forward(node_features, adjacency, training=False)
        
        # Dot product similarity
        emb1 = embeddings[node1_idx]
        emb2 = embeddings[node2_idx]
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2) + 1e-8)
        
        # Sigmoid to get probability
        prob = 1 / (1 + np.exp(-similarity))
        return prob
    
    def get_node_embeddings(
        self,
        node_features: np.ndarray,
        adjacency: np.ndarray
    ) -> np.ndarray:
        """Get learned node embeddings"""
        return self.forward(node_features, adjacency, training=False)


class RelationshipAnalyzer:
    """
    Analyzes relationships in financial networks using GNNs.
    """
    
    def __init__(self, embedding_dim: int = 64):
        self.logger = logging.getLogger("relationship_analyzer")
        self.embedding_dim = embedding_dim
        self.gnn: Optional[GraphNeuralNetwork] = None
        self.graph: Optional[PortfolioGraph] = None
    
    def build_model(self, input_dim: int):
        """Build GNN model"""
        self.gnn = GraphNeuralNetwork(
            layer_dims=[input_dim, 128, 64, self.embedding_dim],
            dropout=0.1
        )
    
    def analyze_portfolio_network(
        self,
        graph: PortfolioGraph
    ) -> Dict[str, Any]:
        """Analyze portfolio network structure"""
        self.graph = graph
        
        features, node_ids = graph.get_node_features_matrix()
        adj, _ = graph.get_adjacency_matrix()
        
        # Build model if needed
        if self.gnn is None:
            self.build_model(features.shape[1])
        
        # Get embeddings
        embeddings = self.gnn.get_node_embeddings(features, adj)
        
        # Network statistics
        degrees = np.sum(adj > 0, axis=1)
        clustering = self._calculate_clustering_coefficients(adj)
        
        # Find clusters using embeddings
        clusters = self._cluster_embeddings(embeddings, node_ids)
        
        # Centrality measures
        centrality = self._calculate_centrality(adj, node_ids)
        
        return {
            'num_nodes': len(node_ids),
            'num_edges': len(graph.edges),
            'avg_degree': np.mean(degrees),
            'max_degree': np.max(degrees),
            'avg_clustering': np.mean(clustering),
            'clusters': clusters,
            'centrality': centrality,
            'embedding_dim': self.embedding_dim
        }
    
    def _calculate_clustering_coefficients(
        self,
        adj: np.ndarray
    ) -> np.ndarray:
        """Calculate local clustering coefficients"""
        n = adj.shape[0]
        clustering = np.zeros(n)
        
        for i in range(n):
            neighbors = np.where(adj[i] > 0)[0]
            k = len(neighbors)
            
            if k < 2:
                continue
            
            # Count edges between neighbors
            subgraph = adj[np.ix_(neighbors, neighbors)]
            triangles = np.sum(subgraph) / 2
            
            possible = k * (k - 1) / 2
            clustering[i] = triangles / possible if possible > 0 else 0
        
        return clustering
    
    def _cluster_embeddings(
        self,
        embeddings: np.ndarray,
        node_ids: List[str],
        n_clusters: int = 5
    ) -> Dict[int, List[str]]:
        """Cluster nodes based on embeddings"""
        # Simple k-means clustering
        n = len(node_ids)
        n_clusters = min(n_clusters, n)
        
        # Random initialization
        centroids = embeddings[np.random.choice(n, n_clusters, replace=False)]
        
        for _ in range(10):  # 10 iterations
            # Assign to nearest centroid
            distances = np.zeros((n, n_clusters))
            for c in range(n_clusters):
                distances[:, c] = np.linalg.norm(embeddings - centroids[c], axis=1)
            
            labels = np.argmin(distances, axis=1)
            
            # Update centroids
            for c in range(n_clusters):
                mask = labels == c
                if np.sum(mask) > 0:
                    centroids[c] = np.mean(embeddings[mask], axis=0)
        
        # Group nodes by cluster
        clusters = {}
        for i, label in enumerate(labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(node_ids[i])
        
        return clusters
    
    def _calculate_centrality(
        self,
        adj: np.ndarray,
        node_ids: List[str]
    ) -> Dict[str, Dict[str, float]]:
        """Calculate various centrality measures"""
        n = len(node_ids)
        
        # Degree centrality
        degree = np.sum(adj > 0, axis=1) / (n - 1)
        
        # Eigenvector centrality (power iteration)
        eigenvector = np.ones(n) / np.sqrt(n)
        for _ in range(100):
            eigenvector = adj @ eigenvector
            norm = np.linalg.norm(eigenvector)
            if norm > 0:
                eigenvector = eigenvector / norm
        
        centrality = {}
        for i, node_id in enumerate(node_ids):
            centrality[node_id] = {
                'degree': float(degree[i]),
                'eigenvector': float(eigenvector[i])
            }
        
        return centrality
    
    def find_similar_assets(
        self,
        asset_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find assets most similar to given asset"""
        if self.graph is None or self.gnn is None:
            return []
        
        features, node_ids = self.graph.get_node_features_matrix()
        adj, _ = self.graph.get_adjacency_matrix()
        
        if asset_id not in node_ids:
            return []
        
        # Get embeddings
        embeddings = self.gnn.get_node_embeddings(features, adj)
        
        target_idx = node_ids.index(asset_id)
        target_emb = embeddings[target_idx]
        
        # Calculate similarities
        similarities = []
        for i, node_id in enumerate(node_ids):
            if node_id == asset_id:
                continue
            
            sim = np.dot(target_emb, embeddings[i]) / (
                np.linalg.norm(target_emb) * np.linalg.norm(embeddings[i]) + 1e-8
            )
            similarities.append({
                'asset_id': node_id,
                'similarity': float(sim),
                'is_neighbor': node_id in self.graph.adjacency.get(asset_id, [])
            })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities[:top_k]
    
    def predict_future_correlations(
        self,
        graph: PortfolioGraph,
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Predict future correlations (link prediction)"""
        features, node_ids = graph.get_node_features_matrix()
        adj, _ = graph.get_adjacency_matrix()
        
        if self.gnn is None:
            self.build_model(features.shape[1])
        
        predictions = []
        n = len(node_ids)
        
        for i in range(n):
            for j in range(i + 1, n):
                # Skip existing edges
                if adj[i, j] > 0:
                    continue
                
                prob = self.gnn.predict_link(features, adj, i, j)
                
                if prob >= threshold:
                    predictions.append({
                        'asset1': node_ids[i],
                        'asset2': node_ids[j],
                        'probability': float(prob),
                        'predicted_edge': True
                    })
        
        # Sort by probability
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        return predictions
