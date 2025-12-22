"""
Augmented Reality Portfolio Visualization
==========================================

Advanced 3D and AR visualization for portfolio analysis:
- WebXR-compatible 3D portfolio views
- Interactive asset bubbles with size = allocation, color = performance
- Real-time animated data flows
- VR/AR headset support
- Mobile AR with camera overlay

Uses Three.js/Babylon.js backends with Python data processing.
"""

import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import math
import colorsys
from abc import ABC, abstractmethod


class VisualizationMode(Enum):
    """Visualization modes supported"""
    DESKTOP_3D = "desktop_3d"
    WEBXR_VR = "webxr_vr"
    WEBXR_AR = "webxr_ar"
    MOBILE_AR = "mobile_ar"
    HOLOGRAPHIC = "holographic"


class SceneLayout(Enum):
    """3D scene layout types"""
    BUBBLE_CLUSTER = "bubble_cluster"
    TREEMAP_3D = "treemap_3d"
    NETWORK_GRAPH = "network_graph"
    SOLAR_SYSTEM = "solar_system"
    CITY_SKYLINE = "city_skyline"
    LANDSCAPE = "landscape"


@dataclass
class Asset3D:
    """3D representation of an asset"""
    symbol: str
    name: str
    asset_class: str
    
    # Position in 3D space
    position: Tuple[float, float, float] = (0, 0, 0)
    
    # Size represents allocation
    size: float = 1.0
    base_size: float = 1.0
    
    # Color represents performance
    color: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    
    # Animation properties
    velocity: Tuple[float, float, float] = (0, 0, 0)
    rotation: Tuple[float, float, float] = (0, 0, 0)
    pulse_intensity: float = 0.0
    
    # Data properties
    allocation_pct: float = 0.0
    performance_1d: float = 0.0
    performance_mtd: float = 0.0
    performance_ytd: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    
    # Metadata
    sector: str = ""
    region: str = ""
    risk_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'asset_class': self.asset_class,
            'position': {'x': self.position[0], 'y': self.position[1], 'z': self.position[2]},
            'size': self.size,
            'color': {'r': self.color[0], 'g': self.color[1], 'b': self.color[2]},
            'velocity': {'x': self.velocity[0], 'y': self.velocity[1], 'z': self.velocity[2]},
            'rotation': {'x': self.rotation[0], 'y': self.rotation[1], 'z': self.rotation[2]},
            'pulse_intensity': self.pulse_intensity,
            'metrics': {
                'allocation_pct': self.allocation_pct,
                'performance_1d': self.performance_1d,
                'performance_mtd': self.performance_mtd,
                'performance_ytd': self.performance_ytd,
                'volatility': self.volatility,
                'sharpe_ratio': self.sharpe_ratio
            },
            'metadata': {
                'sector': self.sector,
                'region': self.region,
                'risk_score': self.risk_score
            }
        }


@dataclass
class Connection3D:
    """3D connection between assets (correlation, flow)"""
    source_symbol: str
    target_symbol: str
    connection_type: str  # 'correlation', 'sector', 'flow'
    strength: float  # 0-1
    color: Tuple[float, float, float] = (0.5, 0.5, 0.5)
    animated: bool = True
    bidirectional: bool = True


@dataclass
class PortfolioScene3D:
    """Complete 3D scene for portfolio visualization"""
    scene_id: str
    created_at: datetime
    layout: SceneLayout
    mode: VisualizationMode
    
    # Scene elements
    assets: List[Asset3D] = field(default_factory=list)
    connections: List[Connection3D] = field(default_factory=list)
    
    # Camera settings
    camera_position: Tuple[float, float, float] = (0, 50, 100)
    camera_target: Tuple[float, float, float] = (0, 0, 0)
    camera_fov: float = 60.0
    
    # Lighting
    ambient_light: float = 0.3
    directional_lights: List[Dict[str, Any]] = field(default_factory=list)
    
    # Animation settings
    auto_rotate: bool = True
    rotation_speed: float = 0.001
    enable_physics: bool = True
    
    # Interactivity
    enable_hover: bool = True
    enable_click: bool = True
    enable_drag: bool = True
    
    # AR-specific
    ar_plane_detection: bool = True
    ar_scale: float = 0.01
    ar_anchor_type: str = "floor"
    
    def to_json(self) -> str:
        return json.dumps({
            'scene_id': self.scene_id,
            'created_at': self.created_at.isoformat(),
            'layout': self.layout.value,
            'mode': self.mode.value,
            'assets': [a.to_dict() for a in self.assets],
            'connections': [
                {
                    'source': c.source_symbol,
                    'target': c.target_symbol,
                    'type': c.connection_type,
                    'strength': c.strength,
                    'color': {'r': c.color[0], 'g': c.color[1], 'b': c.color[2]},
                    'animated': c.animated
                }
                for c in self.connections
            ],
            'camera': {
                'position': {'x': self.camera_position[0], 'y': self.camera_position[1], 'z': self.camera_position[2]},
                'target': {'x': self.camera_target[0], 'y': self.camera_target[1], 'z': self.camera_target[2]},
                'fov': self.camera_fov
            },
            'lighting': {
                'ambient': self.ambient_light,
                'directional': self.directional_lights
            },
            'animation': {
                'auto_rotate': self.auto_rotate,
                'rotation_speed': self.rotation_speed,
                'enable_physics': self.enable_physics
            },
            'interaction': {
                'hover': self.enable_hover,
                'click': self.enable_click,
                'drag': self.enable_drag
            },
            'ar': {
                'plane_detection': self.ar_plane_detection,
                'scale': self.ar_scale,
                'anchor_type': self.ar_anchor_type
            }
        }, indent=2)


class ARPortfolioVisualizer:
    """
    Main class for AR/3D portfolio visualization.
    
    Generates WebXR-compatible scene data that can be rendered
    in browsers with AR/VR capabilities.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("ar_visualization")
        self.scenes: Dict[str, PortfolioScene3D] = {}
        
        # Color mapping for performance
        self.performance_colors = {
            'strong_positive': (0.0, 0.8, 0.2),   # Green
            'positive': (0.4, 0.8, 0.4),
            'neutral': (0.5, 0.5, 0.5),            # Gray
            'negative': (0.8, 0.4, 0.4),
            'strong_negative': (0.8, 0.0, 0.0)    # Red
        }
        
        # Sector colors
        self.sector_colors = {
            'Technology': (0.0, 0.6, 1.0),
            'Healthcare': (0.0, 0.8, 0.6),
            'Financials': (0.2, 0.4, 0.8),
            'Consumer Discretionary': (1.0, 0.6, 0.0),
            'Consumer Staples': (0.8, 0.6, 0.4),
            'Energy': (0.9, 0.3, 0.1),
            'Materials': (0.6, 0.4, 0.2),
            'Industrials': (0.5, 0.5, 0.6),
            'Utilities': (0.4, 0.6, 0.8),
            'Real Estate': (0.6, 0.4, 0.6),
            'Communication': (0.8, 0.2, 0.6)
        }
        
    def performance_to_color(self, performance: float) -> Tuple[float, float, float]:
        """Convert performance percentage to RGB color"""
        if performance > 5:
            return self.performance_colors['strong_positive']
        elif performance > 0:
            # Gradient from neutral to positive
            t = min(performance / 5, 1)
            return self._lerp_color(
                self.performance_colors['neutral'],
                self.performance_colors['positive'],
                t
            )
        elif performance > -5:
            # Gradient from negative to neutral
            t = (performance + 5) / 5
            return self._lerp_color(
                self.performance_colors['negative'],
                self.performance_colors['neutral'],
                t
            )
        else:
            return self.performance_colors['strong_negative']
    
    def _lerp_color(self, c1: Tuple, c2: Tuple, t: float) -> Tuple[float, float, float]:
        """Linear interpolation between two colors"""
        return (
            c1[0] + (c2[0] - c1[0]) * t,
            c1[1] + (c2[1] - c1[1]) * t,
            c1[2] + (c2[2] - c1[2]) * t
        )
    
    def create_bubble_cluster_layout(
        self,
        portfolio_data: pd.DataFrame,
        center: Tuple[float, float, float] = (0, 0, 0),
        radius: float = 50
    ) -> List[Asset3D]:
        """
        Create bubble cluster layout where:
        - Bubble size = allocation weight
        - Bubble color = performance
        - Position = clustered by sector
        """
        assets = []
        sectors = portfolio_data['sector'].unique()
        sector_angles = {s: (2 * math.pi * i / len(sectors)) for i, s in enumerate(sectors)}
        
        for _, row in portfolio_data.iterrows():
            # Calculate position based on sector clustering
            sector = row.get('sector', 'Other')
            base_angle = sector_angles.get(sector, 0)
            
            # Add some randomness within sector cluster
            angle = base_angle + np.random.uniform(-0.3, 0.3)
            distance = radius * (0.5 + np.random.uniform(0, 0.5))
            
            x = center[0] + distance * math.cos(angle)
            z = center[2] + distance * math.sin(angle)
            y = center[1] + np.random.uniform(-10, 10)
            
            # Size based on allocation
            allocation = row.get('allocation_pct', 1)
            size = max(1, allocation * 10)  # Scale factor
            
            # Color based on performance
            performance = row.get('performance_ytd', 0)
            color = self.performance_to_color(performance)
            
            # Pulse intensity based on recent activity/volatility
            volatility = row.get('volatility', 0)
            pulse = min(1, volatility / 50)  # Normalize
            
            asset = Asset3D(
                symbol=row['symbol'],
                name=row.get('name', row['symbol']),
                asset_class=row.get('asset_class', 'equity'),
                position=(x, y, z),
                size=size,
                base_size=size,
                color=color,
                pulse_intensity=pulse,
                allocation_pct=allocation,
                performance_1d=row.get('performance_1d', 0),
                performance_mtd=row.get('performance_mtd', 0),
                performance_ytd=performance,
                volatility=volatility,
                sharpe_ratio=row.get('sharpe_ratio', 0),
                sector=sector,
                region=row.get('region', 'US'),
                risk_score=row.get('risk_score', 0)
            )
            assets.append(asset)
        
        return assets
    
    def create_treemap_3d_layout(
        self,
        portfolio_data: pd.DataFrame,
        width: float = 100,
        depth: float = 100,
        max_height: float = 50
    ) -> List[Asset3D]:
        """
        Create 3D treemap layout where:
        - Floor area = allocation weight
        - Height = performance
        - Color = sector
        """
        assets = []
        total_allocation = portfolio_data['allocation_pct'].sum()
        
        # Sort by allocation for better treemap packing
        sorted_data = portfolio_data.sort_values('allocation_pct', ascending=False)
        
        # Simple row-based layout
        current_x = -width / 2
        current_z = -depth / 2
        row_height = 0
        max_row_width = width
        
        for _, row in sorted_data.iterrows():
            allocation = row.get('allocation_pct', 1)
            normalized = allocation / total_allocation
            
            # Calculate block dimensions
            block_width = math.sqrt(normalized * width * depth)
            block_depth = block_width
            
            # Check if we need new row
            if current_x + block_width > width / 2:
                current_x = -width / 2
                current_z += row_height + 2
                row_height = 0
            
            row_height = max(row_height, block_depth)
            
            # Height based on performance
            performance = row.get('performance_ytd', 0)
            height = max(1, (performance + 50) / 100 * max_height)  # Normalize -50% to +50%
            
            x = current_x + block_width / 2
            z = current_z + block_depth / 2
            y = height / 2
            
            current_x += block_width + 2
            
            # Color based on sector
            sector = row.get('sector', 'Other')
            color = self.sector_colors.get(sector, (0.5, 0.5, 0.5))
            
            asset = Asset3D(
                symbol=row['symbol'],
                name=row.get('name', row['symbol']),
                asset_class=row.get('asset_class', 'equity'),
                position=(x, y, z),
                size=block_width,
                base_size=block_width,
                color=color,
                allocation_pct=allocation,
                performance_ytd=performance,
                sector=sector
            )
            assets.append(asset)
        
        return assets
    
    def create_solar_system_layout(
        self,
        portfolio_data: pd.DataFrame,
        center: Tuple[float, float, float] = (0, 0, 0)
    ) -> List[Asset3D]:
        """
        Create solar system layout where:
        - Center = Total portfolio value
        - Orbit distance = risk/volatility
        - Planet size = allocation
        - Orbit speed = momentum
        """
        assets = []
        
        # Sort by volatility for orbit assignment
        sorted_data = portfolio_data.sort_values('volatility', ascending=True)
        
        for i, (_, row) in enumerate(sorted_data.iterrows()):
            volatility = row.get('volatility', 10)
            orbit_radius = 20 + (volatility * 2)  # Scale volatility to orbit distance
            
            # Initial position on orbit
            angle = (2 * math.pi * i) / len(sorted_data)
            x = center[0] + orbit_radius * math.cos(angle)
            z = center[2] + orbit_radius * math.sin(angle)
            y = center[1]
            
            # Orbit speed based on momentum
            momentum = row.get('momentum', 0)
            orbit_speed = 0.01 + abs(momentum) * 0.001
            
            # Size based on allocation
            allocation = row.get('allocation_pct', 1)
            size = max(2, allocation * 5)
            
            # Color based on performance
            performance = row.get('performance_ytd', 0)
            color = self.performance_to_color(performance)
            
            asset = Asset3D(
                symbol=row['symbol'],
                name=row.get('name', row['symbol']),
                asset_class=row.get('asset_class', 'equity'),
                position=(x, y, z),
                size=size,
                base_size=size,
                color=color,
                velocity=(orbit_speed, 0, 0),  # Orbital velocity
                allocation_pct=allocation,
                performance_ytd=performance,
                volatility=volatility
            )
            assets.append(asset)
        
        return assets
    
    def create_network_graph_layout(
        self,
        portfolio_data: pd.DataFrame,
        correlation_matrix: pd.DataFrame,
        correlation_threshold: float = 0.5
    ) -> Tuple[List[Asset3D], List[Connection3D]]:
        """
        Create force-directed network graph where:
        - Nodes = assets
        - Edges = correlations above threshold
        - Edge thickness = correlation strength
        """
        # Use force-directed positioning
        n_assets = len(portfolio_data)
        positions = self._force_directed_layout(
            correlation_matrix, 
            n_iterations=100,
            k=50
        )
        
        assets = []
        connections = []
        
        for i, (_, row) in enumerate(portfolio_data.iterrows()):
            symbol = row['symbol']
            pos = positions[i]
            
            allocation = row.get('allocation_pct', 1)
            size = max(2, allocation * 5)
            
            performance = row.get('performance_ytd', 0)
            color = self.performance_to_color(performance)
            
            asset = Asset3D(
                symbol=symbol,
                name=row.get('name', symbol),
                asset_class=row.get('asset_class', 'equity'),
                position=(pos[0], pos[1], pos[2]),
                size=size,
                base_size=size,
                color=color,
                allocation_pct=allocation,
                performance_ytd=performance,
                sector=row.get('sector', '')
            )
            assets.append(asset)
        
        # Create connections based on correlations
        symbols = portfolio_data['symbol'].tolist()
        for i in range(n_assets):
            for j in range(i + 1, n_assets):
                if symbols[i] in correlation_matrix.columns and symbols[j] in correlation_matrix.columns:
                    corr = correlation_matrix.loc[symbols[i], symbols[j]]
                    if abs(corr) >= correlation_threshold:
                        # Color based on positive/negative correlation
                        if corr > 0:
                            color = (0.2, 0.6, 0.2)  # Green for positive
                        else:
                            color = (0.6, 0.2, 0.2)  # Red for negative
                        
                        connection = Connection3D(
                            source_symbol=symbols[i],
                            target_symbol=symbols[j],
                            connection_type='correlation',
                            strength=abs(corr),
                            color=color,
                            animated=True
                        )
                        connections.append(connection)
        
        return assets, connections
    
    def _force_directed_layout(
        self,
        correlation_matrix: pd.DataFrame,
        n_iterations: int = 100,
        k: float = 50,
        temperature: float = 100
    ) -> List[Tuple[float, float, float]]:
        """
        Calculate force-directed layout positions.
        Uses correlation to determine attractive forces.
        """
        n = len(correlation_matrix)
        
        # Initialize random positions
        positions = np.random.uniform(-50, 50, (n, 3))
        velocities = np.zeros((n, 3))
        
        cooling_rate = temperature / n_iterations
        
        for iteration in range(n_iterations):
            forces = np.zeros((n, 3))
            
            for i in range(n):
                for j in range(n):
                    if i != j:
                        diff = positions[i] - positions[j]
                        dist = np.linalg.norm(diff) + 0.1  # Avoid division by zero
                        
                        # Repulsive force (all nodes repel)
                        repulsion = k * k / dist
                        forces[i] += (diff / dist) * repulsion
                        
                        # Attractive force (based on correlation)
                        symbols = correlation_matrix.columns.tolist()
                        if i < len(symbols) and j < len(symbols):
                            corr = abs(correlation_matrix.iloc[i, j])
                            if corr > 0.3:
                                attraction = dist * dist / k * corr
                                forces[i] -= (diff / dist) * attraction
            
            # Update positions with temperature cooling
            current_temp = max(1, temperature - iteration * cooling_rate)
            velocities = velocities * 0.5 + forces * 0.1
            
            # Limit velocity
            max_displacement = current_temp
            for i in range(n):
                velocity_magnitude = np.linalg.norm(velocities[i])
                if velocity_magnitude > max_displacement:
                    velocities[i] = velocities[i] / velocity_magnitude * max_displacement
            
            positions += velocities
        
        return [(float(p[0]), float(p[1]), float(p[2])) for p in positions]
    
    def create_city_skyline_layout(
        self,
        portfolio_data: pd.DataFrame,
        width: float = 200
    ) -> List[Asset3D]:
        """
        Create city skyline layout where:
        - Building width = allocation
        - Building height = market cap or value
        - Building color = sector
        """
        assets = []
        n_assets = len(portfolio_data)
        spacing = width / (n_assets + 1)
        
        sorted_data = portfolio_data.sort_values('sector')
        
        for i, (_, row) in enumerate(sorted_data.iterrows()):
            x = -width/2 + spacing * (i + 1)
            
            allocation = row.get('allocation_pct', 1)
            building_width = max(3, allocation * 3)
            
            # Height based on market cap or performance
            market_cap = row.get('market_cap', 0)
            if market_cap > 0:
                height = 10 + math.log10(market_cap / 1e9) * 10  # Log scale
            else:
                height = 10 + row.get('performance_ytd', 0) * 0.5
            height = max(5, height)
            
            y = height / 2
            z = 0
            
            sector = row.get('sector', 'Other')
            color = self.sector_colors.get(sector, (0.5, 0.5, 0.5))
            
            asset = Asset3D(
                symbol=row['symbol'],
                name=row.get('name', row['symbol']),
                asset_class=row.get('asset_class', 'equity'),
                position=(x, y, z),
                size=building_width,
                base_size=building_width,
                color=color,
                allocation_pct=allocation,
                sector=sector
            )
            assets.append(asset)
        
        return assets
    
    def generate_scene(
        self,
        portfolio_data: pd.DataFrame,
        layout: SceneLayout = SceneLayout.BUBBLE_CLUSTER,
        mode: VisualizationMode = VisualizationMode.DESKTOP_3D,
        correlation_matrix: Optional[pd.DataFrame] = None
    ) -> PortfolioScene3D:
        """
        Generate complete 3D scene for portfolio visualization.
        
        Args:
            portfolio_data: DataFrame with columns:
                - symbol, name, sector, asset_class
                - allocation_pct, performance_1d, performance_mtd, performance_ytd
                - volatility, sharpe_ratio, risk_score
            layout: Scene layout type
            mode: Visualization mode (desktop, VR, AR)
            correlation_matrix: Optional correlation matrix for network layouts
            
        Returns:
            PortfolioScene3D object with all scene data
        """
        import uuid
        scene_id = str(uuid.uuid4())
        
        connections = []
        
        if layout == SceneLayout.BUBBLE_CLUSTER:
            assets = self.create_bubble_cluster_layout(portfolio_data)
        elif layout == SceneLayout.TREEMAP_3D:
            assets = self.create_treemap_3d_layout(portfolio_data)
        elif layout == SceneLayout.SOLAR_SYSTEM:
            assets = self.create_solar_system_layout(portfolio_data)
        elif layout == SceneLayout.NETWORK_GRAPH and correlation_matrix is not None:
            assets, connections = self.create_network_graph_layout(
                portfolio_data, correlation_matrix
            )
        elif layout == SceneLayout.CITY_SKYLINE:
            assets = self.create_city_skyline_layout(portfolio_data)
        else:
            assets = self.create_bubble_cluster_layout(portfolio_data)
        
        # Set camera based on layout
        if layout == SceneLayout.CITY_SKYLINE:
            camera_position = (-100, 50, 150)
        elif layout == SceneLayout.SOLAR_SYSTEM:
            camera_position = (0, 100, 150)
        else:
            camera_position = (0, 50, 100)
        
        # Add default lighting
        directional_lights = [
            {'position': [100, 100, 100], 'intensity': 0.8, 'color': [1, 1, 1]},
            {'position': [-100, 50, -50], 'intensity': 0.4, 'color': [0.8, 0.9, 1]}
        ]
        
        scene = PortfolioScene3D(
            scene_id=scene_id,
            created_at=datetime.now(),
            layout=layout,
            mode=mode,
            assets=assets,
            connections=connections,
            camera_position=camera_position,
            camera_target=(0, 0, 0),
            camera_fov=60.0,
            ambient_light=0.3,
            directional_lights=directional_lights,
            auto_rotate=True,
            rotation_speed=0.001,
            enable_physics=layout == SceneLayout.NETWORK_GRAPH,
            ar_plane_detection=mode in [VisualizationMode.WEBXR_AR, VisualizationMode.MOBILE_AR],
            ar_scale=0.01,
            ar_anchor_type="floor"
        )
        
        self.scenes[scene_id] = scene
        self.logger.info(f"Generated 3D scene {scene_id} with {len(assets)} assets")
        
        return scene
    
    def get_webxr_config(self, scene: PortfolioScene3D) -> Dict[str, Any]:
        """Generate WebXR configuration for browser rendering"""
        return {
            'scene': json.loads(scene.to_json()),
            'webxr': {
                'enabled': scene.mode in [VisualizationMode.WEBXR_VR, VisualizationMode.WEBXR_AR],
                'mode': 'immersive-vr' if scene.mode == VisualizationMode.WEBXR_VR else 'immersive-ar',
                'features': {
                    'local-floor': True,
                    'bounded-floor': True,
                    'hand-tracking': True,
                    'hit-test': scene.mode == VisualizationMode.WEBXR_AR
                }
            },
            'renderer': {
                'antialias': True,
                'shadows': True,
                'tone_mapping': 'ACESFilmic',
                'exposure': 1.0
            },
            'controls': {
                'enable_vr_controllers': scene.mode == VisualizationMode.WEBXR_VR,
                'enable_hand_tracking': True,
                'enable_gaze': True
            }
        }
    
    def generate_ar_markers(self, scene: PortfolioScene3D) -> Dict[str, Any]:
        """Generate AR marker data for mobile AR visualization"""
        return {
            'scene_id': scene.scene_id,
            'markers': [
                {
                    'id': f"marker_{asset.symbol}",
                    'symbol': asset.symbol,
                    'type': 'qr_code',
                    'data': asset.to_dict()
                }
                for asset in scene.assets
            ],
            'ar_config': {
                'scale': scene.ar_scale,
                'anchor_type': scene.ar_anchor_type,
                'plane_detection': scene.ar_plane_detection,
                'lighting_estimation': True,
                'shadow_catcher': True
            }
        }
    
    def update_scene_data(
        self,
        scene_id: str,
        updates: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Update scene with new data (real-time updates).
        
        Args:
            scene_id: Scene identifier
            updates: Dict of {symbol: {field: value}}
            
        Returns:
            Success status
        """
        if scene_id not in self.scenes:
            return False
        
        scene = self.scenes[scene_id]
        
        for asset in scene.assets:
            if asset.symbol in updates:
                update = updates[asset.symbol]
                
                if 'performance_ytd' in update:
                    asset.performance_ytd = update['performance_ytd']
                    asset.color = self.performance_to_color(update['performance_ytd'])
                
                if 'allocation_pct' in update:
                    asset.allocation_pct = update['allocation_pct']
                    asset.size = max(1, update['allocation_pct'] * 10)
                
                if 'volatility' in update:
                    asset.volatility = update['volatility']
                    asset.pulse_intensity = min(1, update['volatility'] / 50)
        
        return True
    
    def export_for_unity(self, scene: PortfolioScene3D) -> Dict[str, Any]:
        """Export scene data in Unity-compatible format"""
        return {
            'version': '1.0',
            'scene': {
                'name': f"Portfolio_{scene.scene_id}",
                'prefabs': [
                    {
                        'prefab_id': f"Asset_{asset.symbol}",
                        'prefab_type': 'sphere' if scene.layout == SceneLayout.BUBBLE_CLUSTER else 'cube',
                        'transform': {
                            'position': asset.position,
                            'rotation': asset.rotation,
                            'scale': (asset.size, asset.size, asset.size)
                        },
                        'material': {
                            'color': asset.color,
                            'emission': asset.pulse_intensity * 0.5,
                            'metallic': 0.5,
                            'smoothness': 0.8
                        },
                        'components': [
                            {
                                'type': 'AssetData',
                                'data': asset.to_dict()
                            },
                            {
                                'type': 'InteractableObject',
                                'hover_scale': 1.2,
                                'click_action': 'ShowDetails'
                            }
                        ]
                    }
                    for asset in scene.assets
                ],
                'connections': [
                    {
                        'source': conn.source_symbol,
                        'target': conn.target_symbol,
                        'line_renderer': {
                            'width': conn.strength * 0.5,
                            'color': conn.color,
                            'material': 'animated_line' if conn.animated else 'static_line'
                        }
                    }
                    for conn in scene.connections
                ]
            },
            'ar_foundation': {
                'enabled': scene.mode == VisualizationMode.MOBILE_AR,
                'plane_manager': scene.ar_plane_detection,
                'anchor_manager': True,
                'ar_scale': scene.ar_scale
            }
        }


class RealTimeSceneUpdater:
    """Handles real-time updates to 3D scenes via WebSocket"""
    
    def __init__(self, visualizer: ARPortfolioVisualizer):
        self.visualizer = visualizer
        self.subscribers: Dict[str, List[callable]] = {}
        self.update_buffer: Dict[str, List[Dict]] = {}
        self.batch_interval = 0.1  # 100ms batching
        
    async def subscribe(self, scene_id: str, callback: callable):
        """Subscribe to scene updates"""
        if scene_id not in self.subscribers:
            self.subscribers[scene_id] = []
        self.subscribers[scene_id].append(callback)
    
    async def push_update(self, scene_id: str, updates: Dict[str, Any]):
        """Push update to all subscribers"""
        if scene_id not in self.update_buffer:
            self.update_buffer[scene_id] = []
        
        self.update_buffer[scene_id].append(updates)
    
    async def flush_updates(self):
        """Flush batched updates to subscribers"""
        import asyncio
        
        while True:
            await asyncio.sleep(self.batch_interval)
            
            for scene_id, updates in self.update_buffer.items():
                if updates and scene_id in self.subscribers:
                    # Merge updates
                    merged = {}
                    for update in updates:
                        for symbol, data in update.items():
                            if symbol not in merged:
                                merged[symbol] = {}
                            merged[symbol].update(data)
                    
                    # Apply to scene
                    self.visualizer.update_scene_data(scene_id, merged)
                    
                    # Notify subscribers
                    for callback in self.subscribers[scene_id]:
                        await callback(merged)
                    
                    self.update_buffer[scene_id] = []


# Streamlit component integration
def render_3d_portfolio_streamlit(scene: PortfolioScene3D) -> str:
    """
    Generate HTML/JS code for rendering 3D portfolio in Streamlit.
    Uses Three.js for rendering.
    """
    scene_json = scene.to_json()
    
    html = f"""
    <div id="portfolio-3d-container" style="width: 100%; height: 600px;"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script>
        const sceneData = {scene_json};
        
        // Initialize Three.js scene
        const container = document.getElementById('portfolio-3d-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x1a1a2e);
        
        const camera = new THREE.PerspectiveCamera(
            sceneData.camera.fov,
            container.clientWidth / container.clientHeight,
            0.1, 1000
        );
        camera.position.set(
            sceneData.camera.position.x,
            sceneData.camera.position.y,
            sceneData.camera.position.z
        );
        
        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(container.clientWidth, container.clientHeight);
        renderer.shadowMap.enabled = true;
        container.appendChild(renderer.domElement);
        
        // Add controls
        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        
        // Add lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, sceneData.lighting.ambient);
        scene.add(ambientLight);
        
        sceneData.lighting.directional.forEach(light => {{
            const dirLight = new THREE.DirectionalLight(
                new THREE.Color(light.color[0], light.color[1], light.color[2]),
                light.intensity
            );
            dirLight.position.set(light.position[0], light.position[1], light.position[2]);
            dirLight.castShadow = true;
            scene.add(dirLight);
        }});
        
        // Add assets
        const assetMeshes = {{}};
        sceneData.assets.forEach(asset => {{
            const geometry = new THREE.SphereGeometry(asset.size, 32, 32);
            const material = new THREE.MeshStandardMaterial({{
                color: new THREE.Color(asset.color.r, asset.color.g, asset.color.b),
                metalness: 0.3,
                roughness: 0.7,
                emissive: new THREE.Color(asset.color.r * 0.2, asset.color.g * 0.2, asset.color.b * 0.2),
                emissiveIntensity: asset.pulse_intensity
            }});
            
            const mesh = new THREE.Mesh(geometry, material);
            mesh.position.set(asset.position.x, asset.position.y, asset.position.z);
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            mesh.userData = asset;
            
            scene.add(mesh);
            assetMeshes[asset.symbol] = mesh;
        }});
        
        // Add connections
        sceneData.connections.forEach(conn => {{
            const sourceMesh = assetMeshes[conn.source];
            const targetMesh = assetMeshes[conn.target];
            if (sourceMesh && targetMesh) {{
                const points = [sourceMesh.position, targetMesh.position];
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const material = new THREE.LineBasicMaterial({{
                    color: new THREE.Color(conn.color.r, conn.color.g, conn.color.b),
                    linewidth: conn.strength * 2,
                    transparent: true,
                    opacity: 0.6
                }});
                const line = new THREE.Line(geometry, material);
                scene.add(line);
            }}
        }});
        
        // Animation loop
        let time = 0;
        function animate() {{
            requestAnimationFrame(animate);
            time += 0.016;
            
            // Pulse animation
            Object.values(assetMeshes).forEach(mesh => {{
                if (mesh.userData.pulse_intensity > 0) {{
                    const scale = 1 + Math.sin(time * 3) * mesh.userData.pulse_intensity * 0.1;
                    mesh.scale.setScalar(scale);
                }}
            }});
            
            // Auto rotate if enabled
            if (sceneData.animation.auto_rotate) {{
                scene.rotation.y += sceneData.animation.rotation_speed;
            }}
            
            controls.update();
            renderer.render(scene, camera);
        }}
        
        animate();
        
        // Handle resize
        window.addEventListener('resize', () => {{
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        }});
        
        // Tooltip on hover
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        
        container.addEventListener('mousemove', (event) => {{
            const rect = container.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / container.clientWidth) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / container.clientHeight) * 2 + 1;
            
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(Object.values(assetMeshes));
            
            if (intersects.length > 0) {{
                const asset = intersects[0].object.userData;
                container.title = `${{asset.symbol}}: ${{asset.metrics.performance_ytd.toFixed(2)}}% YTD`;
            }} else {{
                container.title = '';
            }}
        }});
    </script>
    """
    
    return html
